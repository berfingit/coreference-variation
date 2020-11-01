#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import codecs
import pprint 
import copy 
import sys
from nltk import Tree


#tw_conll_path="/Users/berfin/A03/COLING_2020/boundary_corrections_20200320_berfin/corrected_conll_all/"
prp_pos_list={"my", "your", "his" , "her" , "its", "our", "their","ur"}
prp_1st_person_singular_list={"i","me","mine","myself","my","im"}
prp_1st_person_plural_list={"we", "us",  "ourselves", "'s", "ours","our"}
prp_2nd_person_list={"you", "yourself", "yourselves", "yours", "y'all", "your","u","ur","youre","ya","youu"}
prp_3rd_person_singular_list={"he", "she", "it", "him", "her", "himself", "herself",
"itself","his","hers","its","hes","shes"}
prp_3rd_person_plural_list={"they", "them", "themselves","their","theirs","em"}
prp_pers_list=[]
def findPronounAntecedentPairs(tw_conll_path):
    prp_pers_list.extend(prp_1st_person_singular_list)
    prp_pers_list.extend(prp_1st_person_plural_list)
    prp_pers_list.extend(prp_2nd_person_list)
    prp_pers_list.extend(prp_3rd_person_singular_list)
    prp_pers_list.extend(prp_3rd_person_plural_list)

    #TODO:We should exclude John himself kind of constructions
    #keeps the line numbers, not the token numbers of the pronouns and antecedents
    prp_antecedent_pairs={}
    for tw_conll_file in  os.listdir(tw_conll_path):
        prp_antecedent_pairs_per_file=[]
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        #print(tw_conll_file)
        
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        line_order=0
        for line_order in range(0,len(f_conll_lines)):
            #print(line)
            line=f_conll_lines[line_order]
            if("#begin" in line):
                continue
            if("#end" in line):
                continue
            if("\n" == line):
                continue

            line_attributes=line.split('\t')
            if(line_attributes[12]!='-' and line_attributes[11]=='-' and ("(" in line_attributes[12])):
                print("missing type for a mention:", line_attributes[3],line_attributes[11],line_attributes[12])
           
            if("ppers/anaphora" in line_attributes[11] or "ppos/anaphora" in line_attributes[11]):
                '''
                if(line_attributes[3].lower() not in prp_pers_list):
                    print("other pronoun:", line_attributes[3],line_attributes[11],line_attributes[12])
                else:
                    print("standard pronoun:",line_attributes[3],line_attributes[11],line_attributes[12])
                '''
                if(line_attributes[3].lower() in prp_3rd_person_singular_list or line_attributes[3].lower() in
                prp_3rd_person_plural_list):
                    #print("3rd_Pers_Pronoun:",line_attributes[3],line_attributes[11],line_attributes[12])  
                    pronoun_for_distance=line_attributes[3]
                    coref_id=line_attributes[12]
                    if("|" in coref_id):
                        coref_id_list=coref_id.split("|")
                        complete_coref_id=False
                        for candidate_id in coref_id_list:
                            if("(" in candidate_id and ")" in candidate_id):
                                if(complete_coref_id==True):
                                    print("more_than_1_complete_id",candidate_id)
                                else:
                                    complete_coref_id=True
                                pronoun_coref_id=candidate_id[candidate_id.index("(")+1:candidate_id.index(")")]
                    else:
                        pronoun_coref_id=coref_id[coref_id.index("(")+1:coref_id.index(")")]
                    pronoun_token_order=line_order
                    #find the antecedent id
                    antecedent_token_order="-1"
                    for antecedent_order in range(line_order-1,0,-1):
                        antecedent_line_tmp=f_conll_lines[antecedent_order]
                        if("#begin" in antecedent_line_tmp):
                            continue
                        if("#end" in antecedent_line_tmp):
                            continue
                        if("\n" == antecedent_line_tmp):
                            continue
                        
                        antecedent_line_tmp_attributes=antecedent_line_tmp.split("\t")
                        antecedent_coref_tmp=antecedent_line_tmp_attributes[12]
                        antecedent_coref_id_tmp=-1
                        if(antecedent_coref_tmp=="-"):
                            continue
                        elif(antecedent_coref_tmp == "("+pronoun_coref_id+")" or antecedent_coref_tmp == "("+pronoun_coref_id):
                            antecedent_token_order=antecedent_order
                            break
                        elif("|" in antecedent_coref_tmp):
                            found_in_merged_coref=False
                            antecedent_coref_tmp_list=antecedent_coref_tmp.split("|")
                            for id_str in antecedent_coref_tmp_list:
                                if(id_str == "("+pronoun_coref_id+")" or id_str == "("+pronoun_coref_id):
                                    antecedent_token_order=antecedent_order
                                    found_in_merged_coref=True
                                    break
                            if(found_in_merged_coref):
                                break

                        else:
                            #this should be the closing bracket for a mention, so shouldn't take into account for
                            #antecedent detection
                            pass
                    prp_antecedent_pairs_per_file.append((pronoun_token_order,antecedent_token_order))        
        prp_antecedent_pairs[tw_conll_file]=prp_antecedent_pairs_per_file                
        f_conll.close()
    pprint.pprint(prp_antecedent_pairs)
    return prp_antecedent_pairs
                    

def addReferentType2Conll():
        tw_conll_v2="tw_conll_v2/"+tw_conll_file[0,tw_conll_file.index("._")+1]+"_gold_conll"
        f_tw_conll_lines=f_conll.readlines()

def computeTokenDistance(prp_antecedent_pairs, autoUsernames):
    #find token distance
    avg_token_dist_corpus=0
    avg_token_dist_all_files={}
    token_dist_all_files={}
    token_dist_total=0
    considered_pair_count=0
    for tw_conll_file in prp_antecedent_pairs:
        avg_token_dist_file=0
        token_dist_all_file=[]
    
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
       
        for pair in prp_antecedent_pairs[tw_conll_file]:
            prp_order=int(pair[0])
            ant_order=int(pair[1])
            token_dist_pair=0
            if(ant_order!=-1):
                considered_pair_count+=1
                for i in range(ant_order,prp_order):
                    #don't count auto inserted usernames
                    if i in autoUsernames[tw_conll_file]:
                        continue
                        #pass
                    elif "#begin" in f_conll_lines[i]:
                        continue
                    elif "#end" in f_conll_lines[i]:
                        continue
                    elif f_conll_lines[i]=='\n':
                        continue
                    line_attrs=f_conll_lines[i].split('\t')
                    #don't count the discourse markers (UH)
                    if line_attrs[4]=='UH':
                        continue
                    #don't count the emojis
                    if line_attrs[3]=='%emoji':
                        continue
                    #don't count the hashtags
                    if line_attrs[3].startswith('#'):
                        continue
                    #don't count the links 
                    if line_attrs[3].startswith('http'):
                        continue
                    #else:
                    token_dist_pair+=1
                token_dist_all_file.append(token_dist_pair)
                token_dist_total+=token_dist_pair
            else:
                continue
        if(len(token_dist_all_file)!=0):
            avg_token_dist_file=sum(token_dist_all_file)/len(token_dist_all_file)
        avg_token_dist_all_files[tw_conll_file]=avg_token_dist_file
        token_dist_all_files[tw_conll_file]=token_dist_all_file
    avg_token_dist_corpus=token_dist_total/considered_pair_count
    f_token_dist=open("token_distance_tw.txt","w")
    for tw_conll_file in token_dist_all_files:
        for dist in token_dist_all_files[tw_conll_file]:
            f_token_dist.write(str(dist)+",tw\n")
    f_token_dist.close()

    #pprint.pprint(avg_token_dist_all_files)
    print("token_dist_all_files")
    #pprint.pprint(token_dist_all_files)
    print(avg_token_dist_corpus)
    

def computeClauseDistance(prp_antecedent_pairs, clause_boundaries):
    #find token distance
    avg_clause_dist_corpus=0
    avg_clause_dist_all_files={}
    clause_dist_all_files={}
    clause_dist_total=0
    considered_pair_count=0
    for tw_conll_file in prp_antecedent_pairs:
        avg_clause_dist_file=0
        clause_dist_all_file=[]
    
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        clause_boundaries_file=clause_boundaries[tw_conll_file]
        for pair in prp_antecedent_pairs[tw_conll_file]:
            prp_order=int(pair[0])
            ant_order=int(pair[1])
            clause_dist_pair=0
            prp_on_boundary=False
            ant_on_boundary=False
            if(ant_order!=-1):
                considered_pair_count+=1
                for clause_boundary in clause_boundaries_file:
                    if "begin" in clause_boundary and prp_order>=clause_boundaries_file[clause_boundary] and ant_order<=clause_boundaries_file[clause_boundary]:
                        clause_dist_pair+=1
                        if(prp_order==clause_boundaries_file[clause_boundary]):
                            prp_on_boundary=True
                        if(ant_order==clause_boundaries_file[clause_boundary]):
                            ant_on_boundary=True   
                if(prp_on_boundary and ant_on_boundary):
                    print("both are on boundaries", tw_conll_file, pair)
                    clause_dist_pair-=1
                clause_dist_all_file.append(clause_dist_pair)
                clause_dist_total+=clause_dist_pair
            else:
                continue
        f_conll.close()
        if(len(clause_dist_all_file)!=0):
            avg_clause_dist_file=sum(clause_dist_all_file)/len(clause_dist_all_file)
        avg_clause_dist_all_files[tw_conll_file]=avg_clause_dist_file
        clause_dist_all_files[tw_conll_file]=clause_dist_all_file
    avg_clause_dist_corpus=clause_dist_total/considered_pair_count
    pprint.pprint(avg_clause_dist_all_files)
    print("clause_dist_all_files")
    #pprint.pprint(clause_dist_all_files)
    f_cls_dist=open("clause_distance_tw.txt","w")
    for tw_conll_file in clause_dist_all_files:
        for dist in clause_dist_all_files[tw_conll_file]:
            f_cls_dist.write(str(dist)+",tw\n")
    f_cls_dist.close()
    print(avg_clause_dist_corpus)

def findAutoUsernames(tw_conll_path):
    
    token_count_sum=0
    token_count_no_autouser=0
    emoji_count=0
    link_count=0
    hashtag_count=0
    auto_username_count=0
    conll_auto_usernames={}
    for tw_conll_file in  os.listdir(tw_conll_path):
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        #print(tw_conll_file)

        eligibleAutoUsername=False
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        auto_usernames=[]
        for i in range(0,len(f_conll_lines)):
            line=f_conll_lines[i]
            #print(line)
            if("#begin" in line):
                eligibleAutoUsername=True
            elif("#end" in line):
                eligibleAutoUsername=True
            elif("\n" == line):
                eligibleAutoUsername=True
            else:
                line_attrs=line.split('\t')
                token_str=line_attrs[3]
                token_count_sum+=1
                if(token_str.startswith('@') and eligibleAutoUsername):
                    auto_usernames.append(i)
                    auto_username_count+=1
                else:
                    eligibleAutoUsername=False
                if(token_str == '%emoji'):
                    emoji_count+=1
                elif(token_str.startswith('http')):
                    link_count+=1
                elif(token_str.startswith('#')):
                    hashtag_count+=1
        conll_auto_usernames[tw_conll_file]=auto_usernames
        f_conll.close()
    #the disctionaty contain the line numbers not the token numbers
    #pprint.pprint(conll_auto_usernames)
    token_count_no_autouser=token_count_sum-auto_username_count
    print("token_count_sum",token_count_sum)
    print("token_count_no_autouser",token_count_no_autouser)
    print("emoji_count",emoji_count)
    print("link_count",link_count)
    print("hashtag_count",hashtag_count)
    print("auto_username_count",auto_username_count)
    
    return conll_auto_usernames

def findClauseBoundaries(tw_conll_path):
    cl_list_corpus={}
    prn_count_corpus=0
    sentence_count_corpus=0
    clause_count_corpus=0
    prn_list_corpus={}
    for tw_conll_file in  os.listdir(tw_conll_path):
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        #print(tw_conll_file)
        cl_list={}
        clx_count=1
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        clx_tmp=''
        sentence_count=1
        for i in range(0,len(f_conll_lines)):
            prev_line=f_conll_lines[i-1]
            line=f_conll_lines[i]
            if("#begin" in line):
                continue
            elif("#end" in line):
                continue
            elif("\n" == line):
                sentence_count+=1
                sentence_count_corpus+=1
                continue
            else:
                line_attrs=line.split('\t')
                cl_attr=line_attrs[13]
                cl_attr=cl_attr.strip()
                #automatically assigned syntax tag
                syn_attr=line_attrs[5]
                try:
                    syn_attr_prev_line=prev_line.split('\t')[5]
                except: 
                    syn_attr_prev_line="-"
                if(cl_attr!='-'):
                    if("|" in cl_attr):
                        cl_mult=cl_attr.split("|")
                    else:
                        cl_mult=[cl_attr]
                    for cl in cl_mult:
                        cl=cl.strip()
                        if(cl=='CLX'):
                            if(clx_tmp==''):
                                cl+=str(clx_count)
                                clx_tmp=cl
                                clx_count+=1
                            else:
                                cl=clx_tmp.strip()
                                clx_tmp=''
                        elif('CLX' in cl):
                            cl+="_"+str(sentence_count)
                        if(cl+"_begin" in cl_list and cl+"_end" in cl_list):
                            print(line)
                            print("problem in CL naming")
                        elif cl+"_begin" in cl_list:
                            cl_list[cl+"_end"]=i
                        else:
                            cl_list[cl+"_begin"]=i
                else:
                    continue
        cl_list_corpus[tw_conll_file]=cl_list

        f_conll.close()
    #find Paranthetical clauses and exclude them in cl_list, if necessary
    cl_list_tmp=copy.deepcopy(cl_list_corpus)
    for tw_conll_file in cl_list_corpus:
        prn_list={}
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        for cl in cl_list_corpus[tw_conll_file]:
            cl_end=cl.split("_b")[0]+"_end"
            cl_line_nr=cl_list_corpus[tw_conll_file][cl]
            #count the prn clauses, we need to consider syntactic tag of cl's begin line and also the previous line
            #because sometimes stanford parse starts the marking of the clause from the punctuation (usually comma)
            #before the cl starts which we prefer to include the span of the previous clause.
            if("_begin" in cl):
                line=f_conll_lines[cl_line_nr]
                prev_line=f_conll_lines[cl_line_nr-1]
                try:
                    if("PRN" in line.split("\t")[5] or "PRN" in prev_line.split("\t")[5]):
                        prn_list[cl]=cl_line_nr
                        prn_list[cl_end]=cl_list_corpus[tw_conll_file][cl_end]
                        prn_count_corpus+=1
                        #remove PRNs from cl_list_corpus
                        del cl_list_tmp[tw_conll_file][cl]
                        del cl_list_tmp[tw_conll_file][cl_end]
                        clause_count_corpus-=1
                except:
                    pass
            prn_list_corpus[tw_conll_file]=prn_list

    #this part is for error detection (CLs without end boundaries)
    for filename in cl_list_corpus:
        for cl in cl_list_corpus[filename]:
            cl_end=cl.split("_")[0]+"_end"
            #count the clauses
            if("_begin" in cl):
                clause_count_corpus+=1
            #if("_begin" in cl and cl_end not in cl_list_corpus[filename] and "CLX" not in cl):
            if("_begin" in cl and cl_end not in cl_list_corpus[filename]):
                print(filename,cl,cl_list_corpus[filename][cl])
    cl_list_corpus=cl_list_tmp
    print("cl_list_corpus")
    #pprint.pprint(cl_list_corpus)
    print("sentence_count_corpus", sentence_count_corpus)
    print("clause_count_corpus", clause_count_corpus)
    print("prn_count_corpus", prn_count_corpus)

    return cl_list_corpus,prn_list_corpus 


def findNPBoundaries(tw_conll_path,isLarge,prn_boundaries):
    np_list_corpus={}
    np_count=0
    np_count_in_prn=0
    for tw_conll_file in  os.listdir(tw_conll_path):
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        print(tw_conll_file)
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        np_list={}
        np_tmp=''
        for i in range(0,len(f_conll_lines)):
            line=f_conll_lines[i]
            print(line)
            if("#begin" in line):
                continue
            elif("#end" in line):
                continue
            elif("\n" == line):
                continue
            else:
                line_attrs=line.split('\t')
                if(isLarge):
                    np_attr=line_attrs[15]
                else:
                    np_attr=line_attrs[14]
                np_attr=np_attr.strip()
                if(np_attr!='-'):
                    if("|" in np_attr):
                        np_attr_list=np_attr.split("|")
                    else:
                        np_attr_list=[np_attr]

                    for np_attr in np_attr_list:
                        np_attr=np_attr.strip()
                        if("()" in np_attr):
                            np_count+=1
                            np_list[np_attr.split("(")[0]+str(np_count)+"_begin"]=i
                            np_list[np_attr.split("(")[0]+str(np_count)+"_end"]=i
                        elif("(" in np_attr):
                            np_count+=1
                            if(np_tmp!=''):
                                print("problem1",tw_conll_file,np_tmp,np_tmp_2,i)
                            np_tmp=np_attr.split("(")[0]+str(np_count)
                            np_list[np_tmp+"_begin"]=i
                        elif(")" in np_attr):
                            np_tmp_2=np_attr.split(")")[1]+str(np_count)
                            if(np_tmp!=np_tmp_2):
                                print("problem",tw_conll_file,np_tmp,np_tmp_2,i)
                            else:
                                np_list[np_tmp+"_end"]=i
                            np_tmp=''
                        else:
                            print("problem non-standard np_attr", tw_conll_file, np_attr, i)
                else:
                    continue
        for np in np_list:
            if("begin" in np):
                if np.split("_b")[0]+"_end" not in np_list:
                    print("problem basliyor bitmeyor", tw_conll_file, np)
            elif("end" in np):
                if np.split("_e")[0]+"_begin" not in np_list:
                    print("problem baslamadan biteyor",tw_conll_file, np)
        #to exclude NPs in PRN clauses
        prn_list=prn_boundaries[tw_conll_file]
        print("prn_list")
        pprint.pprint(prn_list)
        np_list_tmp=copy.deepcopy(np_list)
        print(np_list_tmp)
        for np_attr in np_list:
            if("_begin" in np_attr):
                np_end=np_attr.split("_b")[0]+"_end"
                for prn_attr in prn_list:
                    if("_begin" in prn_attr):
                        prn_end=prn_attr.split("_b")[0]+"_end"
                        if(np_list[np_attr]>=prn_list[prn_attr] and np_list[np_attr]<=prn_list[prn_end]):
                            print(np_list_tmp[np_attr])
                            del np_list_tmp[np_attr]
                            del np_list_tmp[np_end]
                            np_count_in_prn+=1
                            break
            else:
                continue
        #only the NPs outside of PRN clauses are included in np_list_tmp
        #np_list_corpus[tw_conll_file]=np_list_tmp
        np_list_corpus[tw_conll_file]=np_list
        f_conll.close()
    np_count=np_count-np_count_in_prn
    print("np_list_corpus")
    #pprint.pprint(np_list_corpus)
    print("np_list_corpus_count")
    print(np_count)
    print(np_count_in_prn)
    #TODO: check if any emoji or link is part of an np 

    #exclude trailing username nps from the list
    autoUsernames=findAutoUsernames(tw_conll_path)
    np_list_noautousername=copy.deepcopy(np_list_corpus)
    np_as_username=0
    for tw_conll_file in np_list_corpus:
        for np_attr in np_list_corpus[tw_conll_file]:
            if(np_list_corpus[tw_conll_file][np_attr] in autoUsernames[tw_conll_file]):
                if("begin" in np_attr):
                    del np_list_noautousername[tw_conll_file][np_attr]
                    np_end=np_attr.split("_b")[0]+"_end"
                    del np_list_noautousername[tw_conll_file][np_end]
                    np_as_username+=1
    #print("np_list_noautousername")
    #pprint.pprint(np_list_noautousername)
    print("np_as_username",np_as_username)
    np_updated_count_begin=0
    np_updated_count_end=0
    for tw_conll_file in np_list_noautousername:
        for np_attr in np_list_noautousername[tw_conll_file]:
            if("_begin" in np_attr):
                np_updated_count_begin+=1
            elif("_end" in np_attr):
                np_updated_count_end+=1
            else:
                print("some weird case")
    print("np_updated_count_begin",np_updated_count_begin)
    print("np_updated_count_end",np_updated_count_end)
    return np_list_noautousername

def computeNPDistance(prp_antecedent_pairs, np_boundaries):
    #find token distance
    avg_np_dist_corpus=0
    avg_np_dist_all_files={}
    np_dist_all_files={}
    np_dist_total=0
    considered_pair_count=0
    for tw_conll_file in prp_antecedent_pairs:
        avg_np_dist_file=0
        np_dist_all_file=[]
    
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        np_boundaries_file=np_boundaries[tw_conll_file]
        for pair in prp_antecedent_pairs[tw_conll_file]:
            prp_order=int(pair[0])
            ant_order=int(pair[1])
            np_dist_pair=0
            if(ant_order!=-1):
                considered_pair_count+=1
                for np_boundary in np_boundaries_file:
                    if "begin" in np_boundary and prp_order>np_boundaries_file[np_boundary] and ant_order<np_boundaries_file[np_boundary]:
                        np_dist_pair+=1
                np_dist_all_file.append(np_dist_pair)
                np_dist_total+=np_dist_pair
            else:
                continue
        f_conll.close()
        if(len(np_dist_all_file)!=0):
            avg_np_dist_file=sum(np_dist_all_file)/len(np_dist_all_file)
        avg_np_dist_all_files[tw_conll_file]=avg_np_dist_file
        np_dist_all_files[tw_conll_file]=np_dist_all_file
    avg_np_dist_corpus=np_dist_total/considered_pair_count
    #pprint.pprint(avg_np_dist_all_files)
    #print("np_dist_all_files")
    #pprint.pprint(np_dist_all_files)
    f_np_dist=open("np_distance_tw.txt","w")
    for tw_conll_file in np_dist_all_files:
        for dist in np_dist_all_files[tw_conll_file]:
            f_np_dist.write(str(dist)+",tw\n")
    f_np_dist.close()
    print(avg_np_dist_corpus)

def computeNPHeavyness(tw_conll_path,np_boundaries):
    #TODO: we should exclude the personal pronouns in calculating the heaviness of NPs
    np_length_sum=0
    np_count=0
    ppers_count=0
    np_str_list=open("np_str_list.txt","w+")
    for tw_conll_file in np_boundaries:
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()

        for np_attr in np_boundaries[tw_conll_file]:
            if("_begin" in np_attr):

                np_begin=np_boundaries[tw_conll_file][np_attr]
                np_end=np_boundaries[tw_conll_file][np_attr.split("_b")[0]+"_end"]
                np_length=np_end-np_begin+1
                line_attrs=f_conll_lines[np_begin].split('\t')
                coref_attr=line_attrs[11]
                #exclude personal pronouns in heaviness metrics
                if("ppers" in coref_attr):
                    if(line_attrs[3].lower() not in prp_pers_list):
                        if(np_length!=1):
                            print("long prp",line)
                    ppers_count+=1
                else: 
                    np_count+=1
                    np_length_sum+=np_length
                    np_str=''
                    for i in range(np_begin,np_end+1):
                        np_str+=f_conll_lines[i].split('\t')[3]+' '
                    
                    np_str_list.write("<sent> "+np_str+" </sent>\n")
                    print(tw_conll_file,np_begin,np_length,np_str)
                 
        f_conll.close()
    np_str_list.close()
    print("np_length_sum",np_length_sum)
    print("np_count",np_count)
    print("average_np_length",np_length_sum/np_count)

def calculateAvgNPHeaviness(np_parse_file):
    np_parse_file=open(np_parse_file,"r")
    np_parse_list=np_parse_file.readlines()
    np_height=0
    np_length=0
    np_count=0
    np_tree_all_height=0
    np_height_tw=open("np_height_tw.txt","w")
    np_length_tw=open("np_length_tw.txt","w")

    for np_parse in np_parse_list:
        np_parse_cleaned=np_parse.strip().replace('<parse>','').replace(' </parse>','')
        print(np_parse_cleaned)
        np_tree=Tree.fromstring(np_parse_cleaned)
        if(np_tree.label()=="ROOT"):
            if(len(np_tree)>1):
                print("more_than_1_child",np_tree)
            else:
                np_tree=np_tree[0]
                np_tree_all_height+=np_tree.height()
                if(np_tree.label()=="NP"):
                    np_height+=np_tree.height()
                    np_height_tw.write(str(np_tree.height())+",tw\n")
                    np_length+=len(np_tree.leaves())
                    np_length_tw.write(str(len(np_tree.leaves()))+",tw\n")
                    np_count+=1
                elif (np_tree.label()=="FRAG" or np_tree.label()=="X"):
                    if(len(np_tree)>1):
                        print("FRAG or X with more_than_1_child",np_tree)
                    else:
                        np_tree=np_tree[0]
                        if(np_tree.label()=="NP"):
                            np_height+=np_tree.height()
                            np_height_tw.write(str(np_tree.height())+",tw\n")
                            np_length_tw.write(str(len(np_tree.leaves()))+",tw\n")
                            np_length+=len(np_tree.leaves())
                            np_count+=1
                else:
                    print("another taglabel")
    np_parse_file.close()
    np_height_tw.close()
    np_length_tw.close()
    avg_np_length=np_length/np_count
    avg_np_height=np_height/np_count

    print("considered np_count according to auto_parse",np_count)
    print("avg_np_length according to auto_parse",avg_np_length)
    print("avg_np_height according to auto_parse",avg_np_height)
    print("avg_np_height no filtering",np_tree_all_height/len(np_parse_list))
    

def findSentencesWithNoClause(tw_conll_path):
    sentence_no_clause_corpus=0
    for tw_conll_file in  os.listdir(tw_conll_path):
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        #print(tw_conll_file)

        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        
        eligibleNewSentenceStart=False
        sentence_clauses=[]
        for i in range(0,len(f_conll_lines)):
            line=f_conll_lines[i]
            #print(line)
            if("#begin" in line):
                eligibleNewSentenceStart=True
            elif("#end" in line):
                eligibleNewSentenceStart=False
            elif("\n" == line):
                if(sentence_clauses==[]):
                    sentence_no_clause_corpus+=1                 
                    print("no clause sentence",tw_conll_file,i)
                eligibleNewSentenceStart=True
                sentence_clauses=[]
            else:
                line_attrs=line.split('\t')
                cl_attr=line_attrs[13]
                if(cl_attr.startswith('CL')):
                    sentence_clauses.append(i)
                eligibleNewSentenceStart=False
        f_conll.close()

    print("sentence_no_clause_corpus",sentence_no_clause_corpus)

def computeNPProportions(tw_conll_path,np_boundaries):
    ppers_count=0
    ppos_count=0
    other_np_count=0
    ppers_1st=0
    ppers_2nd=0
    ppers_3rd=0
    #np_boundaries_large=findNPBoundaries(tw_conll_path,True)
    np_begin_attrs={}
    for tw_conll_file in np_boundaries:
        np_begin_attrs[tw_conll_file]={}
        for np_attr in np_boundaries[tw_conll_file]:
            if("_begin" in np_attr):
                np_begin_attrs[tw_conll_file][np_attr]=np_boundaries[tw_conll_file][np_attr]

    for tw_conll_file in  os.listdir(tw_conll_path):
        if("conll" not in tw_conll_file or tw_conll_file.startswith('.')):
            continue
        #print(tw_conll_file)
        
        f_conll=open(tw_conll_path+tw_conll_file,'r')
        f_conll_lines=f_conll.readlines()
        line_order=0
        for line_order in range(0,len(f_conll_lines)):
            #print(line)
            line=f_conll_lines[line_order]
            if("#begin" in line):
                continue
            if("#end" in line):
                continue
            if("\n" == line):
                continue
            if(line_order in np_begin_attrs[tw_conll_file].values()):
                line_attributes=line.split('\t')
                coref_attr=line_attributes[11]
                if("ppers" in coref_attr):
                    if(line_attributes[3].lower() not in prp_pers_list):
                        print("non-standard pro",line_attributes[3])
                    if(line_attributes[3].lower() in prp_1st_person_singular_list or line_attributes[3].lower() in
                    prp_1st_person_plural_list):
                        ppers_1st+=1
                    elif(line_attributes[3].lower() in prp_2nd_person_list):
                        ppers_2nd+=1
                    elif(line_attributes[3].lower() in prp_3rd_person_singular_list or line_attributes[3].lower() in 
                    prp_3rd_person_plural_list):
                        ppers_3rd+=1
                    ppers_count+=1
                elif("ppos" in coref_attr):
                    if(line_attributes[3].lower() in prp_pos_list):
                        print("ppos",line)
                        if(line_attributes[3].lower() in prp_1st_person_singular_list or line_attributes[3].lower() in prp_1st_person_plural_list):
                            ppers_1st+=1
                        elif(line_attributes[3].lower() in prp_2nd_person_list):
                            ppers_2nd+=1
                        elif(line_attributes[3].lower() in prp_3rd_person_singular_list or line_attributes[3].lower() in prp_3rd_person_plural_list):
                            ppers_3rd+=1
                    ppos_count+=1
                else:
                    other_np_count+=1
    print("ppers_count",ppers_count)
    print("ppos_count",ppos_count)
    print("all_prp",ppers_count+ppos_count)
    print("other_np_count",other_np_count)
    print("all_prp perc",(ppers_count+ppos_count)/(ppers_count+ppos_count+other_np_count))
    print("np perc",other_np_count/(ppers_count+ppos_count+other_np_count))
     
    print("ppers_1st",ppers_1st)
    print("ppers_2nd",ppers_2nd)
    print("ppers_3rd",ppers_3rd)

if __name__ == "__main__":
    tw_conll_path=sys.argv[1]
    autoUsernames=findAutoUsernames(tw_conll_path)
    #pprint.pprint(autoUsernames)
    prp_antecedent_pairs=findPronounAntecedentPairs(tw_conll_path)
    #computeTokenDistance(prp_antecedent_pairs,autoUsernames)
    clause_boundaries, prn_boundaries=findClauseBoundaries(tw_conll_path)
    #findSentencesWithNoClause(tw_conll_path)
     
    #computeClauseDistance(prp_antecedent_pairs,clause_boundaries)
    #findSentencesWithNoClause(tw_conll_path)
    np_boundaries=findNPBoundaries(tw_conll_path,True,prn_boundaries)
    #computeNPDistance(prp_antecedent_pairs,np_boundaries)
    #computeNPHeavyness(tw_conll_path,np_boundaries)
    #calculateAvgNPHeaviness("np_parse_list_LS.txt")
    computeNPProportions(tw_conll_path,np_boundaries)
