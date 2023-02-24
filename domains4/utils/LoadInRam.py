import io


class LoadInRam:
    def __init__(self, filename=None):
        self.baos = io.BytesIO()
        if filename:
            self.write_bytes(filename)

    def write_bytes(self, data):
        if isinstance(data, bytes):
            self.baos.write(data)
        elif isinstance(data, str):
            with open(data, 'rb') as f:
                self.baos.write(f.read())

    def get_content(self):
        return self.baos.getvalue().decode()

    def get_byte_array(self):
        return self.baos.getvalue()

    def size(self):
        return self.baos.getbuffer().nbytes

    def reset(self):
        self.baos.truncate(0)
        self.baos.seek(0)

    def close(self):
        self.baos.close()

    def write_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.get_content())
