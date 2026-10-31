"""Independent portfolio adaptation; never executes the original migration script."""
import argparse
import csv
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

CATEGORIES = ('A 物件基本情報', 'B 登記', 'C 測量・境界', 'D 固都税',
              'E 収支・PMレポート', 'F 賃貸借契約・その他契約', 'G 区分所有に関する資料')
SUBFOLDERS = ('01住居','02店舗・事務所','03駐車場','04遊休地','05基本情報','06ホテル','07倉庫','08サブPM物件')
EXTENSIONS = {'.xls','.xlsx','.csv','.docx','.pdf','.doc'}


def relative_folder(root: Path, value: str) -> Path:
    """Confine demo configuration to its workspace, including resolved symlinks."""
    path=Path(value)
    if not value.strip() or path.is_absolute() or path.drive:
        raise ValueError('Use a nonempty relative path')
    resolved=(root/path).resolve()
    if not resolved.is_relative_to(root.resolve()) or resolved == root.resolve():
        raise ValueError('Path must remain below the workspace root')
    return resolved


def eligible(relative: Path, mode='documental') -> bool:
    if relative.name.startswith('~$'):
        return False
    if mode == 'recursive':
        return True
    return (relative.suffix.lower() in EXTENSIONS
            and any(part in SUBFOLDERS for part in relative.parts[:-1])
            and any(part in CATEGORIES for part in relative.parts[:-1]))


def migrate(source: Path, target: Path, *, apply=False, mode='documental'):
    """Yield relative operation records; refuse overlap and existing destinations."""
    source,target=source.resolve(),target.resolve()
    if not source.is_dir():
        raise ValueError('Source directory does not exist')
    if source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError('Source and target must not overlap')
    if mode not in {'documental','recursive'}:
        raise ValueError('Unknown mode')
    if apply:
        target.mkdir(parents=True,exist_ok=True)
        if mode=='documental':
            for category in CATEGORIES:
                destination=target/category
                if destination.resolve().parent != target:
                    raise ValueError('Unsafe category path')
                destination.mkdir(exist_ok=True)
    def walk_error(error):
        raise error
    for folder, dirs, files in os.walk(source,followlinks=False,onerror=walk_error):
        dirs[:]=sorted(d for d in dirs if not (Path(folder)/d).is_symlink())
        for name in sorted(files):
            origin=Path(folder)/name
            rel=origin.relative_to(source)
            if origin.is_symlink() or not origin.resolve().is_relative_to(source) or not eligible(rel,mode):
                continue
            destination=target/rel
            if not destination.resolve().is_relative_to(target):
                yield str(rel),'REJECTED_PATH'
                continue
            if destination.exists():
                yield str(rel),'SKIPPED_EXISTS'
                continue
            if not apply:
                yield str(rel),'DRY_RUN'
                continue
            created=False
            try:
                destination.parent.mkdir(parents=True,exist_ok=True)
                with origin.open('rb') as src, destination.open('xb') as dst:
                    created=True
                    shutil.copyfileobj(src,dst,length=16*1024*1024)
                yield str(rel),'COPIED'
            except OSError as error:
                # Leave any partial new file visible, never silently overwrite it.
                yield str(rel),f'ERROR_{type(error).__name__}'+('_PARTIAL_FILE' if created else '')


def safe_cell(value):
    return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('config/dictionary.example.csv'))
    parser.add_argument('--workspace',type=Path,default=Path('.'))
    parser.add_argument('--apply',action='store_true',help='Copy files; default is preview')
    parser.add_argument('--mode',choices=['documental','recursive'],default='documental')
    args=parser.parse_args()
    root=args.workspace.resolve()
    logdir=root/'logs'
    logdir.mkdir(exist_ok=True)
    log=logdir/f"copy_{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.csv"
    failures=0
    with args.config.open(encoding='utf-8-sig',newline='') as inp, log.open('x',encoding='utf-8-sig',newline='') as out:
        reader=csv.DictReader(inp)
        if reader.fieldnames != ['property','target','source']:
            raise ValueError('CSV header must be property,target,source')
        writer=csv.writer(out)
        writer.writerow(['Property','Relative file','Status','Time UTC'])
        for row in reader:
            source=relative_folder(root,row['source'])
            target=relative_folder(root,row['target'])
            for rel,status in migrate(source,target,apply=args.apply,mode=args.mode):
                writer.writerow([safe_cell(row['property']),safe_cell(rel),status,datetime.now(timezone.utc).isoformat()])
                out.flush()
                failures+=status.startswith(('ERROR','REJECTED'))
    print(f'Log: {log.name}; errors: {failures}')
    return 1 if failures else 0


if __name__=='__main__':
    raise SystemExit(main())
