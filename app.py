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
    flag3 = False
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
        anal.create_dataframe()
        flag3 = True

    if flag3:
        st.write("Количество сообщений в чате", anal.get_messages_amount())
        st.write("Количество сообщений от кажого участника:")
        st.write( anal.get_messages_amount_split())
        st.write('Дата первого сообщения', anal.get_date_of_first_message())
        st.write('Количество дней общения в каждом году:')
        st.write(anal.get_amount_of_talking_days_yearly())
        st.write('Среднее количество слов в сообщении по диалогу', anal.get_word_count_mean())
        st.write('Среднее количество слов в сообщении по каждому участнику:')
        st.write(anal.get_word_count_mean_by_person())
        st.write('Среднее количество слов в сообщении по каждому участнику:')
        offset = st.slider(
            label='Выбери сколько часов после сообщения должно пройти чтобы это считалось новым диалогом',
            min_value=1,
            max_value=40,
            step=1)
        st.write('Количество начатых бесед каждым участником:')
        st.write(anal.get_amount_of_started_conversations(offset))




if __name__ == "__main__":
    main()
