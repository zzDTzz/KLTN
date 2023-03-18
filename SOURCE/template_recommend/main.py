from name_tags import print_name_tag_table
from item_base_collaborative_filtering import recommend_item_template
from user_base_collaborative_filtering import recommend_user_template


if __name__ == '__main__':
    print_name_tag_table('/SOURCE/template_recommend/data/template_with_tags.csv')
    
    roles = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
    
    for item in roles:
        recommend_item_template(item)

    recommend_user_template('/SOURCE/template_recommend/data/clean_template_user_count.csv')