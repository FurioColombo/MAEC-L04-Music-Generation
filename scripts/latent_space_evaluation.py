import os
import glob

import pretty_midi

import numpy as np
import tensorflow as tf

from definitions import ConfigSections
from modules.utilities import config as config_file
from modules.utilities import complexity_measures

logging = tf.compat.v1.logging
script_config = config_file.load_configuration_section(ConfigSections.LATENT_SPACE_SAMPLING)


def run():
    output_dir = os.path.expanduser(script_config.get("output_dir"))
    num_bars = script_config.get("num_bars")

    for idx, file_path in enumerate(glob.iglob(output_dir + '**/*.mid', recursive=True)):
        midi_file = pretty_midi.PrettyMIDI(file_path)
        midi_file = complexity_measures.sanitize(midi_file, num_bars)

        # complexity rating
        note_density = complexity_measures.note_density(midi_file, num_bars, binary=True)
        toussaint = complexity_measures.toussaint(midi_file, num_bars, binary=True)
        pitch_range = complexity_measures.pitch_range(midi_file)
        contour = complexity_measures.contour(midi_file)

        # save current sample complexities file
        folder_path = os.path.dirname(file_path)
        folder_name = os.path.basename(folder_path)
        sample_num = folder_name.split(sep="_")[-1]
        sample_complexities_file_name = 'sample_complexities_%s.npy' % sample_num
        sample_complexities_file_path = os.path.join(folder_path, sample_complexities_file_name)
        sample_complexities = [toussaint, note_density, pitch_range, contour]
        np.save(sample_complexities_file_path, sample_complexities)


def main(_):
    logging.set_verbosity(script_config.get("log"))
    run()


def console_entry_point():
    tf.compat.v1.disable_v2_behavior()
    tf.compat.v1.app.run(main)


if __name__ == '__main__':
    console_entry_point()
