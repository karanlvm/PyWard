# triggers check_pickle_usage
import pickle

with open("data.pkl", "rb") as f:
    obj = pickle.load(f)
