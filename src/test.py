from parser import *


result = get_appeals()

print(result)

for i in result:
    print("===========================NEW THREAD==============================")
    print("url: " + i.get_url())
    print("title: " + i.get_title())
    
    for j in i.get_posts():
        print("\n---------------------------NEW POST--------------------------------")
        print("id: " + j.get_id())
        print(j.get_content())
        print("author: " + j.get_author())
        print("author_url: " + j.get_author_URL())
        print("author_avatar: " + j.get_author_avatar())
        print("time_published: " + str(j.get_time_published()))

    print("\n")
    
print("===================================================================")
