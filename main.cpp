#include <stdio.h>
#include <string>
#include "mstBackbone.h"
#include <iostream>
#include <experimental/filesystem>
// #include <boost/filesystem.hpp>
#include <sys/stat.h>
using namespace std;
namespace fs = std::experimental::filesystem;

int main(int argc, char **argv)
{	
	

	string path_to_alignment_file;
	fs::path alignment_file_path_obj;
	fs::path prefix_path_obj;
    string prefix_for_output_files;
	string path_to_directory;	
    int size_of_subtree;
	bool parallel_comp = 0;
	int int_parallel_comp;
 	struct stat buffer;
	bool flag_alignment_file = 0;
	bool flag_size_of_subtree = 0;
	bool flag_prefix = 0;
    if (argc < 2) {        
        cerr << "Usage: " << argv[0] << " --seq sequence_alignment_file --size size_of_subtree --out prefix_for_output_files --parallel_comp boolflag" << endl;
        return (-1);
    } else {        
        // parse arguments            
        for (int i = 1; i < argc ; i++) {
        // path to multiple sequence alignment file
            if (strcmp(argv[i], "--seq") == 0) {				
                if (i < argc -1) {
					flag_alignment_file = 1;
                    path_to_alignment_file = argv[++i];
					cout << "alignment file name is " << path_to_alignment_file << endl;
					if (stat (path_to_alignment_file.c_str(), &buffer) != 0) { // check if input file exists
						cout << "Please check if the input filename is correct" << endl;
						exit (-1);
					}
					alignment_file_path_obj = path_to_alignment_file;
                }
        // prefix_to_output_files (e.g. prefix is "covid-19_size_42" and the alignment is in directory "/foo/bar/data/")
		// newick file is stored as /foo/bar/data/covid-19_size_42.newick
		// log file is stored as /foo/bar/data/covid-19_size_42.mstbackbone_log
            } else if (strcmp(argv[i], "--out") == 0) {
                if (i < argc -1) {
					flag_prefix = 1;
                    prefix_for_output_files = argv[++i];
					// prefix_for_output_files = alignment_file_path_obj.parent_path().string() + prefix_for_output_files;
					prefix_path_obj =  alignment_file_path_obj.parent_path();
					prefix_path_obj /= prefix_for_output_files;
					cout << "prefix for output files is" << prefix_for_output_files << endl;					
                }
        // size of subtree Vs
            } else if (strcmp(argv[i], "--size") == 0) {
                if (i < argc -1) {
					flag_size_of_subtree = 1;
                    size_of_subtree = stoi(argv[++i]);
                }
			}  else if (strcmp(argv[i], "--parallel_comp") == 0) {
                if (i < argc -1) {
					int_parallel_comp = stoi(argv[++i]);
					// cout << "input for parallel_comp is " << stoi(argv[++i]) << endl;					
					if (int_parallel_comp == 0 || int_parallel_comp == 1) {
						parallel_comp = (bool) int_parallel_comp;
						cout << "flag is either 0 or 1" << endl;
					} else {						
						parallel_comp = 0;
					}                 
                }
			}        
        }

		if (!flag_size_of_subtree) {
			size_of_subtree = 10;
		}

		if (!flag_prefix) {
			prefix_path_obj =  alignment_file_path_obj.parent_path();
			prefix_path_obj /= "mst-backbone_default_output";			
			// prefix_for_output_files = path_obj.parent_path().string() + "mst_backbone";
		}
		cout << "Calling MSTbackbone " << endl;
		MSTBackbone MSTBackboneObj(path_to_alignment_file, size_of_subtree, prefix_path_obj.string(),parallel_comp);
    }

	return 0;
} 
