from simple_aes_cipher import AESCipher, generate_secret_key

class Passworder():
  def __init__(self):

    # TODO:パスフレーズは環境変数から設定するようにする
    pass_phrase = "hogefuga"
    secret_key = generate_secret_key(pass_phrase)

    # generate cipher
    self.cipher = AESCipher(secret_key)


  def _encrypt(self, raw_text):
    return self.cipher.encrypt(raw_text)

  def _decrypt(self, encrypt_text):
    return self.cipher.decrypt(encrypt_text)

