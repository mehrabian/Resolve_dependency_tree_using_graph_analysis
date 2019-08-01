import os
import sys

try:
    import json
except:
    print(' module missing --> module {} does not exit'.format('json'))
    print(' To install {} please run command: pip install {}'.format('json','json'))

try:
    import argparse
except:
    print(' module missing --> module {} does not exit'.format('argparse'))
    print(' To install {} please run command: pip install {}'.format('argparse','argparse'))

class distro:
    """ class to create the directed graph for distributions and dependencies

    :param name: name of the distro to create
    :ivar reqs: link between two distro

    >>> if A depends on B, to make the tree we do
    >>> A=distro('A')
    >>> B=distro('B')
    >>> A.addDepen(B)

    """
    def __init__(self, name):
        self.name = name
        self.reqs = []

    def addDepen(self, distro):
        """ creates dependency between distributions
        """
        self.reqs.append(distro)

def addKey(dict, key):
    """ check if the name "key" is present in the dependency dictionary, and
    if not to add it to the dictionary

    :param dict: dictionary which contains the list of the dependencies
    :param key: name of the new distribution to be added to the dependency
    """
    if key in dict:
        print('The key {} is present and has values {}'.format(key,dict[key]))
    else:
        dict[key]=['empty']

def dep_resolve(distro, fixedDps, remainingDps, distMapper):
    """ recursively find the list of required distributions from the dependency graph

    :param distro: name of the distribution for which the dependency tree should is made
    :param fixedDps: list of the fixed dependencies
    :param remainingDps: list of dependencies which are remaining

    """
    remainingDps.append(distro)
    try:
        #print('distro=',distro,'   reqs=',list(distMapper[distro].reqs))
        for edge in list(distMapper[distro].reqs):
            #print(distro,edge)
            if edge not in fixedDps and edge!='empty':
                if edge in remainingDps:
                    raise Exception('Circular reference detected: {} -> {}'.format(distro, edge))
                dep_resolve(edge, fixedDps, remainingDps,distMapper)
        fixedDps.append(distro)
        remainingDps.remove(distro)
    except KeyError as e:
        print(e)

def merge_two_dicts(x, y):
    """ merge two dictionaries

    :param x: first dictionary
    :param y: second dictionary
    :return z: merged dictionary

    >>> merge_two_dicts({a:{1}},{b:{2}})
    {a:{1},b:{2}}

    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def dir_path(path):
    """ check if the input path is valid

    : param path: path to data directory
    """
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

def main(dNames,dPath):
    """ main function which creates the dependency tree

    :param dNames: list of distros whose dependency tree needs to be resolved
    :param dPath: path to the data folder in which distros are
    :return: the json file for the inputted names

    """

    # remove the log file for the warnings; warnings are redirected into this file
    try:
        os.remove("warnings.log")
    except:
        pass

    # read the list in the core-modules.json file into the coreModules list
    with open(dPath+'core-modules.json', "r") as read_file:
        coreModules= json.load(read_file)

    # read the key-value pairs in module-distro-map.json into a dictionary
    with open(dPath+'module-distro-map.json', "r") as read_file:
        moduleDistroMap= json.load(read_file)

    # get the folder architecture inside the data folder
    arc=os.walk(top=dPath)

    # create the list of subfolders inside the data folder
    dists=[]
    for subdir,dir,f in arc:
        if subdir == dPath:
            dists=dir

    # creat the list of dependencies for each distribution
    dependencies={}
    for dist in dists:
        addKey(dependencies,dist)
        with open(dPath+dist+'/META.json', "r") as read_file:
            data = json.load(read_file)
        try:
            # get the contents of the relevant keys
            mods=data['prereqs']['runtime']['requires']
            for mod,ver in mods.items():
                #print('module:',mod,' version:',ver)
                for modMap,distMap in moduleDistroMap.items():
                    #print(k,v,mod)
                    if modMap == mod and mod not in coreModules:
                        dependencies[dist].append(str(distMap))
        except Exception as e:
            if hasattr(e, 'message'):
                print('--error:',e.message)
            else:
                # record warnings in alog file
                g=open('warnings.log','a')
                g.write('warning: for distribution {}, the key {} does not exists\n'.format(dist,e))
                g.close()

    # map distro names into graph objects
    # convert dependencies into a graph like Tree
    distMapper={}
    for k in dependencies:
        kn=k
        k=distro(k)
        distMapper[kn]=k
        for vi in dependencies[kn]:
            # check is the distro is not added before
            if vi not in k.reqs:
                # add distro into the neighbor list
                k.addDepen(vi)

    # for each name entere in the command linee, the dependency tree is created and concatenated
    # into a dictionary and finally converted to a json file named allDepenTrees
    print(list(dependencies))
    allDepenTrees={}
    for dName in dNames:
        fixedDps=[]
        remainingDps=[]
        dep_resolve(dName,fixedDps,remainingDps,distMapper)
        outTree = {}
        curTree = outTree
        for f in reversed(fixedDps):
            curTree[f] = {}
            curTree = curTree[f]
            allDepenTrees=merge_two_dicts(allDepenTrees,outTree)
    #print('-------------------------------------------------------')
    print(allDepenTrees)
    return allDepenTrees


if __name__ == '__main__':
    # this part is used during the standalone call
    parser = argparse.ArgumentParser(description='1. The program is written in Python. \n' +
    'To run the program you need to have  python3 or higher installed on your system. \n' +
    '  \n'+
    '2. To execute the program run: \n'+
    '  python resolveDependencyTree.py --name [arbitrary number of distribution names] --path [relative path to the data directory] \n'
    '-- example: \n' +
    '    python resolveDependencyTree.py --name DateTime Dist-CheckConflicts --path data/  \n' +
    'Note that for this case the data folder is in the same place as the python code\n' +
    'Code will check for the required packages and if they are not avaible it will print an error message with the guidelines to install it\n' +
    '  \n' +
    '3. Few tests are written for the code which are inside the test_code.py program. To run the test code, execute:\n' +
    '    pytest -vv \n' +
    'Note that for testing the data folder should be in the same folder as the main code.\n' +
    'if pytest is not avaible on your system install it by running:\n' +
    'conda install pytest or pip install pytest)\n')

    parser.add_argument('--name', required=True,nargs='+', type=str, help='list of distro names', action='append')
    parser.add_argument('--path', type=dir_path, default='data/')
    args = parser.parse_args()
    input = vars(args)
    # if multipe inctances of --name is used in the output
    input['name']= [item for sublist in input['name'] for item in sublist]
    print(input)
    main(dNames=input['name'],dPath=input['path'])
else:
    # this part is used during the testing with pytest
    main('Dist-CheckConflicts','data/')
