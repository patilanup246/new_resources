def mongoQuery(collection, query):
    result_list = []
    skip_num = 0
    limit_num = 10000
    while True:
        result_list_one = list(collection.find(query).skip(skip_num).limit(limit_num))
        result_list += result_list_one
        if not result_list_one:
            break
        skip_num += limit_num
        print(skip_num)
    return result_list