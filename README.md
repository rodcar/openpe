# openpe

A library for searching datasets on datosabiertos.gob.pe

## Installation

You can install the package using pip:

```sh
pip install openpe
```

## Usage

Here's a basic example of how to use the library:

```python
import openpe

# Search for datasets
datasets = openpe.search('education')
for dataset in datasets:
    print(dataset['title'])
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the maintainer at ivan@example.com.
