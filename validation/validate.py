import os
import sys

training_file = "location_10_4_a40.log"
testing_file = "location_10_4_a10"

path = os.path.dirname(os.path.realpath(__file__))


def read_train_file(filename=training_file):
    filename = path+"/data/train/"+filename
    ranks = []
    lamda = []
    with open(filename, "rb") as f:
        for line in f:
            l = line.decode("utf-8").strip().replace("\n", "")
            if l.find("Ranking collect:") != -1:
                # print(l)
                rank_string = l.replace("Ranking collect:", "").strip()
                ranks.append([int(x) for x in rank_string.split()])
            if l.find("Lamda:") != -1:
                lamda = [float(theta) for theta in
                         l.replace("Lamda: ", "").strip().split()]

    #print("Number permutations: %d" % len(ranks))
    #print("Ranks[1][2] %d" % ranks[1][2])
    #print("Lamda: %s" % " ".join([str(x) for x in lamda]))
    return ranks, lamda


def read_test_file(filename=testing_file):
    filename = path + "/data/test/" + filename
    choices = []
    pr_choices = []
    with open(filename,"r") as f:
        lines = f.readlines()
        node = int(lines[1])
        n = len(lines)
        for l in lines[4:n:2]:
            choice = [int(x) for x in l.strip().split()]
            choices.append(choice)
        for l in lines[5:n:2]:
            pr_choice = [float(x) for x in l.strip().split()]
            pr_choices.append(pr_choice)
    #print(node)
    #print(sum(pr_choices[-1]))
    #print(choices[-1])
    return node, choices, pr_choices


def is_indecator(index, permutation):
    if permutation[0] == index:
        return 1.0
    return 0.0

def predict(node, choices, ranks, lamda):
    predict_pr_choice =[]


    return predict_pr_choice

if __name__ == '__main__':
    if len(sys.argv) == 3:
        training_file = sys.argv[1]
        testing_file = sys.argv[2]
    else:
        training_file = "location_10_4_a40.log"
        testing_file = "location_10_4_a10"
    path = os.path.dirname(os.path.realpath(__file__))
    ranks, lamda = read_train_file(training_file)
    node, choices, pr_choice = read_test_file(testing_file)