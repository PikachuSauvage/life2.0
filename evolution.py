import sys
import simulation as sim
import pandas as pd
import numpy as np

def evol_master():
    # read the evolution parameters from the config file
    config = sim.read_config_file(INI_file)
    environment_file = config.get('EVOLUTION', 'environment')
    temperature = config.getfloat('EVOLUTION', 'temperature')
    temperature_rate = config.getfloat('EVOLUTION', 'temperature_rate')
    nbiter = config.getint('EVOLUTION', 'nbiter')
    p_inversion = config.getfloat('EVOLUTION', 'p_inversion')
    fitness_file = config.get('EVOLUTION', 'output_file')
    
    pth = INI_file[:-10]
    expected_profile = pd.read_table(pth+environment_file,sep='\t',header=None)[1]
    
    tss, tts, prot, genome_size = sim.load_genome(INI_file)
    gene_expression = sim.start_transcribing(INI_file, output_dir, tss, tts, prot, genome_size)
    fitness = get_fitness(gene_expression, expected_profile)
    
    with open(fitness_file,'w') as f:
        f.write("fitness\tgenome size\tmutation type\n")
        for it in range(nbiter):
            temperature *= temperature_rate
            tss, tts, prot, genome_size, fitness, mutation_type = evol_main_loop(tss, tts, prot, genome_size, fitness, p_inversion, temperature, expected_profile)
            print('fitness : ',fitness)
            # mutation_type is 1 for inversion and 2 for indel
            f.write(str(fitness)+"\t"+str(genome_size)+"\t"+str(mutation_type)+"\n")

    
def evol_main_loop(tss, tts, prot, genome_size, fitness, p_inversion, temperature, expected_profile):
    # making backups for the current genome
    tss_backup = tss.copy()
    tts_backup = tts.copy()
    prot_backup = prot.copy()
    genome_size_backup = genome_size
    fitness_backup = fitness
    
    if np.random.rand() < p_inversion: # decide if there is an inversion or indel
        inversion(tss, tts, prot, genome_size)
        mutation_type = 1
    else:
        genome_size = indel(tss, tts, prot, genome_size)
        mutation_type = 2
    
    print(tss)
    print(tts)
    print(prot)
    gene_expression = sim.start_transcribing(INI_file, output_dir, tss, tts, prot, genome_size)
    fitness = get_fitness(gene_expression, expected_profile)
    
    # if the new fitness is lower than the previous one
    # and the random choice doesn't select the new genome
    # we go back to the backups 
    if fitness < fitness_backup and np.random.rand() > np.exp((fitness-fitness_backup)/temperature):
            tss = tss_backup
            tts = tts_backup
            prot = prot_backup
            genome_size = genome_size_backup
            fitness = fitness_backup
    return (tss, tts, prot, genome_size, fitness, mutation_type)
                
    
def inversion(tss, tts, prot, genome_size):
    correct_positions = False
    while not correct_positions:
        correct_positions = True
        a = np.random.randint(genome_size) + 1
        b = np.random.randint(genome_size) + 1
        for pos in [a,b]:
            for i in range(len(tss['TUindex'])): # check if a position is not inside a transcript
                if tss['TUorient'][i] == '+':
                    if pos > tss['TSS_pos'][i] and pos < tts['TTS_pos'][i]:
                        correct_positions = False
                else:
                    if pos < tss['TSS_pos'][i] and pos > tts['TTS_pos'][i]:
                        correct_positions = False
    min_pos = min([a,b])
    max_pos = max([a,b])
    for i in range(len(tss['TUindex'])): # change transcript's positions and orientation
        if min_pos <= tss['TSS_pos'][i] and max_pos >= tss['TSS_pos'][i]:
            tss.at[i,'TSS_pos'] = min_pos + max_pos - tss['TSS_pos'][i]
            tts.at[i,'TTS_pos'] = min_pos + max_pos - tts['TTS_pos'][i]
            if tss['TUorient'][i] == '+':
                tss.at[i,'TUorient'] = '-'
                tts.at[i,'TUorient'] = '-'
            else:
                tss.at[i,'TUorient'] = '+'
                tts.at[i,'TUorient'] = '+'
    for i in range(len(prot['prot_pos'])):
        if min_pos <= prot['prot_pos'][i] and max_pos >= prot['prot_pos'][i]:
            prot.at[i,'prot_pos'] = min_pos + max_pos - prot['prot_pos'][i]
    
        
def indel(tss, tts, prot, genome_size):
    correct_position = False
    while not correct_position:
        correct_position = True
        pos = np.random.randint(genome_size) + 1
        for i in range(len(tss['TUindex'])):
            if tss['TUorient'][i] == '+':
                if pos >= tss['TSS_pos'][i] and pos <= tts['TTS_pos'][i]:
                    correct_position = False
            else:
                if pos <= tss['TSS_pos'][i] and pos >= tts['TTS_pos'][i]:
                    correct_position = False
    if np.random.rand() < 0.5: # same probability for insertion or deletion
        insertion = 1
    else:
        insertion = -1
    for i in range(len(tss['TUindex'])):
        if pos < tss['TSS_pos'][i]:
            tss.at[i,'TSS_pos'] += insertion
            tts.at[i,'TTS_pos'] += insertion
    deleted_prot = -1
    for i in range(len(prot['prot_pos'])):
        if pos < prot['prot_pos'][i]:
            prot.at[i,'prot_pos'] += insertion
        if pos == prot['prot_pos'][i]:
            deleted_prot = i # check if a barrier is being removed
    if deleted_prot != -1:
        prot.drop(deleted_prot)
        print("Deletion of a protein!!!!!!!!")
    genome_size += insertion
    return genome_size
    
def get_fitness(gene_expression, expected_profile):
    if len(gene_expression) != len(expected_profile):
        print("Error : gene_expression and expected_profile don't have the same length : ",len(gene_expression)," vs ",len(expected_profile))
    total = sum(gene_expression)
    profile = [expression / total for expression in gene_expression]
    distance = sum([np.abs(profile[i]-expected_profile[i]) for i in range(len(profile))])
    return np.exp(-distance) # fitness is exp(-distance) so it's between 0 and 1

    
if __name__ == '__main__':
	INI_file='params.ini'  #sys.argv[1]
	output_dir='output/' #sys.argv[2]
	evol_master()
	
#cat fitness*.txt > pp.txt && R -q -e "x<- read.csv('pp.txt');summary(x);sd(x[,1])"

