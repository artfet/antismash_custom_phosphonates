# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

"""Identify TTA codons in BGCs"""

from antismash.config.args import ModuleArgs
from antismash.modules.tta.tta import detect, TTAResults

NAME = "tta"
SHORT_DESCRIPTION = "TTA detection"
PRIORITY = 1


def get_arguments():
    args = ModuleArgs('Additional analysis', 'tta')
    args.add_analysis_toggle('--tta',
                             dest='tta',
                             action='store_true',
                             default=False,
                             help="Run TTA codon detection module.")
    return args


def check_options(options):
    return []


def check_prereqs():
    """Check for prerequisites"""
    # No external dependencies
    return []


def is_enabled(options):
    """ Should the module be run with these options """
    return options.tta


def regenerate_previous_results(previous, record, options):
    if not previous:
        return None
    return TTAResults.from_json(previous)


def run_on_record(seq_record, results, options):
    if isinstance(results, TTAResults) and results.record_id == seq_record.id:
        return results
    return detect(seq_record, options)
