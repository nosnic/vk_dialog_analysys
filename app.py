import streamlit as st
import analyzer
from importlib import reload
reload(analyzer)

def main():
    st.title("Vk Dialog Analysis")
    st.write("Введите свой access token:")
    token = st.text_input("Access Token")
    flag = False
    flag1 = False
    flag2 = False
    friend_names = []
    friend_dict = {}

    if token:
        try:
            anal = analyzer.VkDialogAnalyzer(token)
            flag = True
            properties = anal.vk_session.users.get(user_ids=anal.friend_list)
            for friend in properties:
                friend_names.append(friend['first_name'] + ' ' + friend['last_name'])
                friend_dict[friend['first_name'] + ' ' + friend['last_name']] = friend['id']
        except Exception as e:
            st.write("Пожалуйста, введите валидный access token.")
    else:
        st.write("Пожалуйста, введите access token.")

    if flag:
        selected_option = st.selectbox("Выберите элементы", friend_names)
        st.write("Выбранный элемент:", selected_option)
        st.write("Его id", friend_dict[selected_option])
        flag2 = True

    if flag2:
        anal.download_vk_dialog(friend_dict[selected_option])
        st.write(anal.dialog)


if __name__ == "__main__":
    main()
