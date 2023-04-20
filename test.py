res = {"a": {"b": {"c": 1}, "d": 4}, "e": 5}
path_list = ["f"]

def find_for_deletion(path_list):
    """
    input: a list of path
    return: -1 if not found
            an index pointing to the key to be deleted

            e.g. 
                path_list = ["a", "b"]
                resp = {"a": {"b": 2}} 
                if we want to delete "b", it will return 0 because we need to delete "a" too

    """
    # resp = main.find_one({"_id": "root"}, {"_id": 0})
    # print(resp)
    result = find_for_deletion_helper(path_list, 0, res)
    print(result)
    if result == False: # we haven't found it
        return -1
    return result[0]

def find_for_deletion_helper(path_list, idx, resp):
    print(str(idx) + " " + str(resp))
    # if not found
    if resp == None:
        return False
    
    # base case
    if idx == len(path_list):
        return [idx, True if type(resp) is not dict or len(resp) == 1 else False]
    
    result = find_for_deletion_helper(path_list, idx+1, resp.get(path_list[idx]))
    
    # if deeper recursion tells us its not found, return False
    if result == False:
        return False

    if len(resp) == 1 and result[1]:
        result[0] = idx
        return result
    
    result[1] = False
    return result

print(find_for_deletion(path_list))