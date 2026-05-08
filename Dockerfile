# Use the official MkDocs Material image — no build step needed.
# Docs: https://hub.docker.com/r/squidfunk/mkdocs-material
FROM squidfunk/mkdocs-material:latest

WORKDIR /wiki

EXPOSE 8080

CMD ["serve", "--dev-addr=0.0.0.0:8080"]
