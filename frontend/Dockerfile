FROM busybox:1.35

# Add a user and switch to it
RUN adduser -D stud
USER stud
WORKDIR /home/stud

# Copy the source files into the container
COPY src/ .

# Set the build-time IP address argument
ARG ip

# Replace the placeholder with the provided IP address
RUN sed -i "s/44.213.66.1/$ip/g" index.html

# Set the entrypoint to busybox and start the HTTP server
ENTRYPOINT ["busybox"]
CMD ["httpd", "-f", "-v", "-p", "3000"]
