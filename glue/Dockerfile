# Use the official AWS Glue 3.0 image as the base
FROM amazon/aws-glue-libs:glue_libs_3.0.0_image_01

# Switch to the root user to get permissions to remove the file
USER root

# Remove the default hive-site.xml that incorrectly points to the AWS Glue Data Catalog.
# This is the key step to force Spark to use a local metastore.
# Note: The path might vary slightly for different Glue versions. This is for Glue 3.0.
RUN rm /home/glue_user/spark/conf/hive-site.xml

# Switch back to the default non-root user for running the job
USER glue_user
