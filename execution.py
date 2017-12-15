from multiprocessing import Pool
import pandas as pd
import scipy
from evolution import evol_master, get_fitness
from simulation import start_transcribing, load_genome, read_config_file


INI = 'params.ini'
tss, tts, prot, genome_size = load_genome(INI)
config = read_config_file(INI)
environment_file = config.get('EVOLUTION', 'environment')
expected_profile = pd.read_table(environment_file,sep='\t',header=None)[1]

def run(output_file):
	scipy.random.seed() 
	gene_expression = start_transcribing(INI, "outputdir",
					                     tss, tts, prot, genome_size)
	fitness = get_fitness(gene_expression, expected_profile)
	with open(output_file, 'w') as f:
		f.write(str(fitness)+'\n')
	

if __name__ == '__main__':
	p = Pool(8)
	p.map(run, ["fitness"+str(i)+".txt" for i in range(8)])






