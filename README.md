# addPicture

Sample AWS API Gateway code from Nature Finder Android app.  

1. Takes in JSON from app with picture inforamtion.  
2. Picture was uploaded to S3 directly from app.  
3. This script then uses the AWS Rekognition API to check the S3 picture for nudity and also provides automated labels for the picture.  
4. The moderation or nudity level is then recorded and the labels are added to the pictures "hashtags" for user searchabilty.
5. The pictures information is then saved in the database and the nudity level is then sent back to the app to let the user know if the picture was uploaded correctly.  
