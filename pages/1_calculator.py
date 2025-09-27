import streamlit as st

# use underscores instead of spaces
number1 = st.number_input("Number 1:")
number2 = st.number_input("Number 2:")

def add(a, b):
    return a + b

st.write("Number 1:", number1)
st.write("Number 2:", number2)

st.write("Sum:", add(number1, number2))
