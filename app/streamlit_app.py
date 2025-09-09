from route_finder.data_loader import load_dataset
from route_finder.ui import main

if __name__ == "__main__":
    df = load_dataset('./east-java-cities-dataset.xlsx')
    main(df)
