# import argparse
# from run import _run, _analyse_run, _select_run
# from lib.common.exceptions import (
#     InvalidPhaseError,
#     SelectorNotFoundError,
#     AnalyserNotFoundError,
#     WorkingDirectorNotFoundError,
# )
# import os
# import shutil
# from unittest import TestCase, mock
#
# # NOTE: defined outside class so it is available in mocks
# OUTFOLDER = "temp"
#
#
# class EntryTestCase(TestCase):
#     @classmethod
#     def setUpClass(self):
#         os.mkdir(OUTFOLDER)
#         self.AN_ANALYSER_PATH = f"{OUTFOLDER}/a_selector/derived/an_analyser"
#         os.makedirs(self.AN_ANALYSER_PATH)
#
#     @classmethod
#     def tearDownClass(self):
#         if os.path.exists(OUTFOLDER):
#             shutil.rmtree(OUTFOLDER)
#
#     @mock.patch(
#         "argparse.ArgumentParser.parse_args",
#         return_value=argparse.Namespace(
#             phase="selector", module="youtube", config={}, folder=f"{OUTFOLDER}/testout"
#         ),
#     )
#     def test_invalid_phase(self, mock_args):
#         with self.assertRaisesRegex(
#             InvalidPhaseError, "must be either 'select' or 'analyse'"
#         ):
#             _run()
#
#     @mock.patch(
#         "argparse.ArgumentParser.parse_args",
#         return_value=argparse.Namespace(
#             phase="select",
#             module="definitelynotaselectorthatexists",
#             config={},
#             folder=f"{OUTFOLDER}",
#         ),
#     )
#     def test_invalid_selector(self, mock_args):
#         with self.assertRaisesRegex(
#             SelectorNotFoundError,
#             "Could not find a valid selector named 'definitelynotaselectorthatexists'",
#         ):
#             _run()
#
#     @mock.patch(
#         "argparse.ArgumentParser.parse_args",
#         return_value=argparse.Namespace(
#             phase="analyse",
#             module="definitelynotananalyserthatexists",
#             config={},
#             folder=f"{OUTFOLDER}",
#         ),
#     )
#     def test_invalid_analyser(self, mock_args):
#         with self.assertRaisesRegex(
#             AnalyserNotFoundError,
#             "Could not find a valid analyser named 'definitelynotananalyserthatexists'",
#         ):
#             _run()
#
#     @mock.patch(
#         "argparse.ArgumentParser.parse_args",
#         return_value=argparse.Namespace(
#             phase="analyse", module="youtube", config={}, folder="bad_folder"
#         ),
#     )
#     def test_invalid_analyser(self, mock_args):
#         with self.assertRaisesRegex(
#             WorkingDirectorNotFoundError, "'bad_folder', does not exist"
#         ):
#             _run()
