import json

class Dataset:
    def __init__(self, id: str, title: str, description: str, categories: list, url: str, modified_date: str, release_date: str, publisher: str, metadata: dict):
        self.id = id
        self.title = title
        self.description = description
        self.categories = categories
        self.url = url
        self.modified_date = modified_date
        self.release_date = release_date
        self.publisher = publisher
        self.metadata = metadata

    def __repr__(self):
        return f"Dataset(id={self.id}, title={self.title}, description={self.description}, categories={self.categories}, url={self.url}, modified_date={self.modified_date}, release_date={self.release_date}, publisher={self.publisher}, metadata={self.metadata})"

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "categories": self.categories,
            "url": self.url,
            "modified_date": self.modified_date,
            "release_date": self.release_date,
            "publisher": self.publisher,
            "metadata": self.metadata
        })