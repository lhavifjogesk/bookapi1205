from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse
from books import get_all_books, get_book_by_id, add_book

class BookHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == "/books":
            self._set_headers()
            self.wfile.write(json.dumps(get_all_books()).encode())
        elif self.path.startswith("/books/"):
            try:
                book_id = int(self.path.split("/")[-1])
                book = get_book_by_id(book_id)
                if book:
                    self._set_headers()
                    self.wfile.write(json.dumps(book).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({ "error": "Book not found" }).encode())
            except ValueError:
                self._set_headers(400)
                self.wfile.write(json.dumps({ "error": "Invalid ID" }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({ "error": "ERO" }).encode())

    def do_POST(self):
        if self.path == "/books":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                if "title" in data and "author" in data:
                    new_book = add_book(data["title"], data["author"])
                    self._set_headers(201)
                    self.wfile.write(json.dumps(new_book).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({ "error": "Missing title or author" }).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({ "error": "Invalid JSON" }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({ "error": "Not found" }).encode())

def run(server_class=HTTPServer, handler_class=BookHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
