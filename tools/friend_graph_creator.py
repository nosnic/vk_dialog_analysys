import vk_api
from streamlit_agraph import Node, Edge, Config


class FriendGraphCreator:
    def __init__(self, token):
        self.valid_friends = []
        self.friend_list = []
        self.user_id = None
        self.user_name = None
        self.user_info = None
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token).get_api()
        self.valid_close_users = set()
        self.valid_close_users_edges = set()
        self.config = Config(
            height=500,
            width=700,
            highlightColor="#F7A7A6",
            directed=False,
            physics=True,
            maxVelocity=1,
            stabilization=True,
            fit=False,
            timestep=0.05
        )

    def set_info(self, user_id):
        self.user_info = self.vk_session.users.get(user_id=user_id)[0]
        self.user_name = f"{self.user_info['first_name']} {self.user_info['last_name']}"
        self.user_id = self.user_info['id']
        self.friend_list = self.vk_session.friends.get(user_id=user_id, order='hints')['items']
        self.valid_friends = self.get_valid_friends(self.friend_list)

    def get_valid_friends(self, friend_list):
        friends_info = self.vk_session.users.get(user_ids=friend_list)
        return [friend['id'] for friend in friends_info if 'deactivated' not in friend and not friend['is_closed']]

    def create_first_level(self):
        mutual_friends = []
        for i in range(0, len(self.valid_friends), 100):
            try:
                mutual_friends.extend(self.vk_session.friends.getMutual(
                    source_uid=self.user_id,
                    target_uids=self.valid_friends[i:i + 100]
                ))
            except vk_api.exceptions.ApiError as e:
                print(e)
        self.valid_close_users = set(self.valid_friends)
        self.valid_close_users_edges = {(user['id'], friend) for user in mutual_friends for friend in user['common_friends']}

    def create_graph(self):
        user_info_dict = {user['id']: f"{user['first_name']} {user['last_name']}" for user in self.vk_session.users.get(user_ids=list(self.valid_close_users))}
        nodes = [Node(id=user_id, size=5, label=user_info_dict[user_id]) for user_id in self.valid_close_users]
        edges = [Edge(str(user_id), str(friend)) for user_id, friend in self.valid_close_users_edges]
        return nodes, edges


    # def parse_friends(self, friends_list):
    #     edges = set()
    #     nodes = set()
    #     for friends_list_dict in friends_list:
    #         for source_friend, target_friends in friends_list_dict.items():
    #             for target_friend_dict in target_friends:
    #                 for target_friend in target_friend_dict['common_friends']:
    #                     if target_friend != self.my_id:
    #                         edges.add((source_friend, target_friend))
    #                         nodes.add(target_friend)
    #     return edges, nodes
    #
    # def create_second_level(self):
    #     res = []
    #     for i in range(0, len(self.valid_friends), 100):
    #         for friend in self.valid_friends:
    #             res.append(
    #                 {
    #                     friend:
    #                         self.vk_session.friends.
    #                         getMutual(source_uid=friend, target_uids=self.valid_friends[:100])
    #                 }
    #             )
    #     edges, nodes = self.parse_friends(res)
    #     self.valid_close_users = self.valid_close_users and nodes
    #     self.valid_close_users_edges = self.valid_close_users_edges and edges
