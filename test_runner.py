# from premiere.testing.utils import KillPGProcessesTestRunner
# from unittest.loader import TestLoader
#
#
# class FuckNutsTestLoader(TestLoader):
#
#     def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
# #
# #         import ipdb;ipdb.set_trace()
# #         top_level_dir = '/Users/andy/dev/overdrive'
#         return super(FuckNutsTestLoader, self).discover(start_dir, pattern, top_level_dir)
#
#
# class SummaTestRunner(KillPGProcessesTestRunner):
#     test_loader = FuckNutsTestLoader()
#
#     def run_tests(self, *args, **kwargs):
#         '''
#         # janky way to pass elementExplorer flag to test runner
#         if [ "$1" == "--elementExplorer" ]; then
#             export ELEMENT_EXPLORER=1
#         fi
#         '''
#         super(SummaTestRunner, self).run_tests(*args, **kwargs)


