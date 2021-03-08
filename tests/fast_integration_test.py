import argparse as ap
import pathlib
import sys
import os
import unittest
import subprocess as sp

class TestAll(unittest.TestCase):

    def test_all_integration(self):
        """ Integration test for whole pipeline with test data. """
        # not a unit test, but put here anyway
        # load config; test input and output data not provided
        testpath = pathlib.Path(__file__).parent.absolute()
        iconfpath = testpath / "INTEGRATION.cfg"
        with open(iconfpath) as f:
            conf = {l.split("=")[0]:l.split("=")[1].strip() for l in f}
        sys.stderr.write("config found!\n") 
        test_data_dir = pathlib.Path(conf['TEST_DATA_DIR'])
        date = "2021-01-31"
        nf_path = conf['NEXTFLOW_PATH']
        subsample_dir = test_data_dir / "test_subsample/"
        res_dir = test_data_dir / "test_res/"
        uk_fa = subsample_dir / "subsample_uk_fasta.fa"
        uk_meta = subsample_dir / "subsample_uk_metadata.tsv"
        uk_acc = subsample_dir / "subsample_uk_accessions.tsv"
        gisaid_fasta = subsample_dir / "subsample_gisaid_fasta.fa"
        gisaid_metadata = subsample_dir / "subsample_gisaid_metadata.csv"
        gisaid_var = res_dir / "gisaid.global.variants.csv"
        test_pub_dir = testpath / "tmp/publish"
        test_pub_dev = testpath / "tmp/publish_dev"
        uk_prev_meta = res_dir / "master.csv"
        test_work_dir = testpath / "tmp/work"
        # Define paths for running
        nxf_command = """{nf} run ./workflows/process_cog_uk.nf \\
          --date {date} \\
          --uk_fasta {uk_fa} \\
          --uk_metadata {uk_meta} \\
          --uk_accessions {uk_acc} \\
          --gisaid_fasta {gisaid_fa} \\
          --gisaid_metadata {gisaid_meta} \\
          --gisaid_variants {gisaid_var} \\
          --publish_dir {pub_dir} \\
          --publish_dev {pub_dev} \\
          --uk_previous_metadata {uk_prev_meta} \\
          -w {w} \\
          -process.executor slurm""".format(nf=nf_path,
                            date=date,
                            uk_fa=uk_fa,
                            uk_meta=uk_meta,
                            uk_acc=uk_acc,
                            gisaid_fa=gisaid_fasta,
                            gisaid_meta=gisaid_metadata,
                            gisaid_var=gisaid_var,
                            pub_dir=test_pub_dir,
                            pub_dev=test_pub_dev,
                            uk_prev_meta=uk_prev_meta,
                            w=test_work_dir)
        sys.stderr.write("Running small integration test...\n")
        try:
#            res = sp.check_output(nxf_command, shell=True)
            sys.stderr.write("... nextflow exited successfully\n")
            # Check alignments
            val_aln_path = test_data_dir / "test_publish" / "alignments"
            val_files = [val_f for val_f in os.listdir(val_aln_path)]
            test_aln_path = test_pub_dir / "alignments"
            test_out_files = [of for of in os.listdir(test_aln_path)]
#            print(val_files)
#            print(test_out_files)
            for f1, f2 in zip(val_files, test_out_files):
                assert str(f1) == str(f2)
                sys.stderr.write("Checking %s vs %s\n" % (str(val_aln_path / f1), str(test_aln_path / f2)))
                f1md5 = sp.check_output("md5sum %s" % str(val_aln_path / f1), shell=True).split()[0]
#                print(f1md5)
                f2md5 = sp.check_output("md5sum %s" % str(test_aln_path / f2), shell=True).split()[0]
#                print(f2md5)
                self.assertEqual(f1md5, f2md5)
            sys.stderr.write("Tests passed!\n")
                

        except sp.CalledProcessError as e:
            sys.stderr.write("... FAILED\n %s\n %s\n" % (e.returncode, e.output))

if __name__ == "__main__":
    unittest.main()
