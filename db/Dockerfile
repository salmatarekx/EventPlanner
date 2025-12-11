FROM mongo:7.0

# Create working directory for data (not recommended but acceptable if required)
RUN mkdir -p /data/db

# Expose MongoDB default port
EXPOSE 27017

# Run MongoDB server
CMD ["mongod", "--bind_ip_all"]
