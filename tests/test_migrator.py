"""Portfolio tests: synthetic files only."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from file_migrator import CATEGORIES, eligible, migrate, relative_folder

class MigrationTests(unittest.TestCase):
    def test_filters(self):
        prefix=Path('01住居')/CATEGORIES[0]
        self.assertTrue(eligible(prefix/'demo.PDF'))
        self.assertFalse(eligible(prefix/'~$demo.xlsx'))
        self.assertFalse(eligible(prefix/'demo.exe'))
        self.assertFalse(eligible(Path('other')/'demo.pdf'))
        self.assertTrue(eligible(Path('other')/'demo.txt','recursive'))

    def test_paths_reject_escape(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): relative_folder(Path(d),'../outside')

    def test_preview_copy_structure_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/'source'
            target=root/'target'
            rel=Path('01住居')/CATEGORIES[0]/'demo.csv'
            (source/rel).parent.mkdir(parents=True)
            (source/rel).write_bytes(b'fictional')
            self.assertEqual(list(migrate(source,target)),[(str(rel),'DRY_RUN')])
            self.assertFalse(target.exists())
            self.assertEqual(list(migrate(source,target,apply=True)),[(str(rel),'COPIED')])
            self.assertEqual((target/rel).read_bytes(),b'fictional')
            self.assertTrue(all((target/c).is_dir() for c in CATEGORIES))
            (source/rel).write_bytes(b'changed')
            self.assertEqual(list(migrate(source,target,apply=True)),[(str(rel),'SKIPPED_EXISTS')])
            self.assertEqual((target/rel).read_bytes(),b'fictional')

    def test_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): list(migrate(Path(d),Path(d)/'nested',apply=True))

if __name__=='__main__': unittest.main()
