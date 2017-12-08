import sys
import simulation as sim

INI_file=sys.argv[1]
output_dir=sys.argv[2]

(tss, tts, prot, genome_size) = sim.load_genome(INI_file)
sim.start_transcribing(INI_file, output_dir, tss, tts, prot, genome_size)
