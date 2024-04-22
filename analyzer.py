import vk_api


class VkDialogAnalyzer:
    def __init__(self, token):
        self.dialog = None
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token).get_api()
        self.messages = None
        self.friend_list = self.vk_session.friends.get(order='hints')['items']
        self.test = 0

    def download_vk_dialog(self, friend_id):
        try:
            messages = self.vk_session.messages.getHistory(user_id=friend_id, count=200)
            all_messages = messages['items']
            while messages['count'] > len(all_messages):
                messages = (self.vk_session.
                            messages.getHistory(user_id=friend_id, count=200, offset=len(all_messages)))
                all_messages.extend(messages['items'])
                self.test = round(len(all_messages)/messages['count'], 2)
                print(round(len(all_messages)/messages['count'], 2))
                self.dialog = all_messages
        except vk_api.VkApiError as error_msg:
            print(error_msg)
