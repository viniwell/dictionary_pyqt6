with open('database.txt', 'r', encoding='UTF-8') as f:
    file_text=f.readlines()


with open('database.txt', '+w', encoding='UTF-8') as file:
    ans=file_text.copy()
    for i in range(len(ans)):
        ans[i]='Unrecorded'+ans[i]
    file.writelines(ans)
    
