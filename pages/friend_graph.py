import streamlit as st
from tools import friend_graph_creator
from importlib import reload
from streamlit_agraph import agraph, Node, Edge, Config

reload(friend_graph_creator)

def main():
    st.title("Vk Friend Graph")
    flag = False
    friend_names = []
    friend_dict = {}
    if st.session_state.token:
        try:
            fri = friend_graph_creator.FriendGraphCreator(st.session_state.token)
            properties = fri.vk_session.users.get(
                user_ids=fri.vk_session.users.get()[0]['id']
            )
            properties.extend(
                fri.vk_session.users.get(user_ids=fri.vk_session.friends.get(order='hints')['items'])
            )
            for friend in properties:
                print(friend)
                friend_names.append(friend['first_name'] + ' ' + friend['last_name'])
                friend_dict[friend['first_name'] + ' ' + friend['last_name']] = friend['id']
            flag = True
        except Exception as e:
            pass
    else:
        st.write("Пожалуйста, введите access token.")

    if flag:
        selected_option = st.selectbox("Выберите элементы", friend_names)
        st.write("Выбранный элемент:", selected_option)
        st.write("Его id", friend_dict[selected_option])
        fri.set_info(int(friend_dict[selected_option]))
        fri.create_first_level()
        nodes, edges = fri.create_graph()
        agraph(nodes=nodes, edges=edges, config=fri.config)

if __name__ == "__main__":
    main()