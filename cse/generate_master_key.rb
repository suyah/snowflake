require 'openssl'
require 'base64'

symmetric_key = OpenSSL::Cipher.new("AES-256-ECB").random_key
master_key = Base64.encode64(symmetric_key)
puts "Master key is: #{master_key}"

# master_key = Base64.strict_encode64(symmetric_key)
# puts master_key


# def get_random_aes_256_gcm_key
#   cipher = OpenSSL::Cipher.new('aes-256-gcm')
#   cipher.encrypt
#   random_key = cipher.random_key
#   random_key_64_string = [random_key].pack('m')
#   random_key_64 = random_key_64_string.unpack('m')[0]
#   puts 'The base 64-encoded string representation of the randomly-' \
#     'generated AES256-GCM key is:'
#   puts random_key_64_string
#   puts 'Keep a record of this key string. You will not be able to later ' \
#     'decrypt the contents of any object that is encrypted with this key ' \
#     'unless you have this key.'
#   return random_key_64
# end

# puts get_random_aes_256_gcm_key