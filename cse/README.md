1. install ruby
2. install bundler: `gem install bundler`
3. run `bundle install`
4. generate key: `bundle exec ruby generate_master_key.rb`
5. encrypt and upload file: `bundle exec ruby s3_file_upload.rb`
