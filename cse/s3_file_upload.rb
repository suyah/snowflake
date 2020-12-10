require 'aws-sdk'
require 'openssl'
require 'base64'

master_key = "cD5dmWZ6N5xj9hOMdG4q/X3jH8c/hS0jkPYKowD3VBw="
bucket_name = "snf-demo-bucket-sse-s3"
file = "./my_data.csv"
decoded_master_key = Base64.decode64(master_key)

def encrypted_object_uploaded?(s3_encryption_client, bucket_name, object_key, object_content)
  s3_encryption_client.put_object(
    bucket: bucket_name,
    key: object_key,
    body: object_content
  )
  return true
rescue StandardError => e
  puts "Error uploading object: #{e.message}"
  return false
end

# def get_decrypted_object_content(s3_encryption_client, bucket_name, object_key)
#   response = s3_encryption_client.get_object(
#     bucket: bucket_name,
#     key: object_key
#   )
#   if defined?(response.body)
#     return response.body.read
#   else
#     return 'Error: Object content empty or unavailable.'
#   end
# rescue StandardError => e
#   return "Error getting object content: #{e.message}"
# end

#s3_encryption_client = Aws::S3::EncryptionV2::Client.new(
#    encryption_key: get_master_key,
#    key_wrap_schema: :aes_gcm, # or :rsa_oaep_sha1 if using RSA
#    content_encryption_schema: :aes_gcm_no_padding,
    # security_profile: :v2
#    security_profile: :v2_and_legacy
#)
s3_encryption_client = Aws::S3::Encryption::Client.new(encryption_key: decoded_master_key)

object_key = File.basename(file)
object_content = File.read(file)

if encrypted_object_uploaded?(s3_encryption_client, bucket_name, object_key, object_content)
  puts 'Uploaded.'
else
  puts 'Not uploaded.'
end

# list 
s3 = Aws::S3::Resource.new
my_bucket = s3.bucket(bucket_name)
my_bucket.objects.each do |obj|
  puts "#{obj.key} => #{obj.etag}"
end

# puts get_decrypted_object_content(
#   s3_encryption_client,
#   bucket_name,
#   file_name
# )
