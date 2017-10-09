# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

"""Gene finding using Prodigal

"""

import logging
from os import path
from helperlibs.wrappers.io import TemporaryDirectory
from helperlibs.bio import seqio
from Bio.SeqFeature import SeqFeature, FeatureLocation

from antismash.common.subprocessing import execute


def run_prodigal(seq_record, options):
    """
        Run progidal to annotate prokaryotic sequences
    """
    if "basedir" in options.get('prodigal', ''):
        basedir = options.prodigal.basedir
    else:
        basedir = ""
    with TemporaryDirectory(change=True):
        name = seq_record.id.lstrip('-')
        if not name:
            name = "unknown"
        fasta_file = '%s.fasta' % name
        result_file = '%s.predict' % name
        with open(fasta_file, 'w') as handle:
            seqio.write([seq_record], handle, 'fasta')

        # run prodigal
        prodigal = [path.join(basedir, 'prodigal')]
        prodigal.extend(['-i', fasta_file, '-f', 'sco', '-o', result_file])
        if options.genefinding_tool == "prodigal-m" or len(seq_record.seq) < 20000:
            prodigal.extend(['-p', 'meta'])

        err = execute(prodigal).stderr
        if err.find('Error') > -1:
            logging.error("Failed to run prodigal: %r", err)
            return
        for line in open(result_file, 'r'):
            # skip first line
            if not line.startswith('>'):
                continue
            name, start, end, prodigal_strand = line[1:].rstrip().split("_")

            try:
                start = int(start)
                end = int(end)
                if prodigal_strand == "+":
                    strand = 1
                else:
                    strand = -1
            except ValueError:
                logging.error('Malformatted prodigal output line %r', line.rstrip())
                continue

            if start > end:
                strand = -1
                start, end = end, start

            loc = FeatureLocation(start-1, end, strand=strand)
            feature = SeqFeature(location=loc, id=name, type="CDS",
                    qualifiers={'locus_tag': ['ctg%s_%s' % (seq_record.record_index, name)]})
            seq_record.features.append(feature)