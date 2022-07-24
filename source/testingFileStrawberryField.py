import strawberryfields as sf
from strawberryfields import ops
import matplotlib.pyplot as plt


# create a 3-mode quantum program
prog = sf.Program(3)

with prog.context as q:
    ops.Sgate(0.54) | q[0]
    ops.Sgate(0.54) | q[1]
    ops.Sgate(0.54) | q[2]
    ops.BSgate(0.43, 0.1) | (q[0], q[2])
    ops.BSgate(0.43, 0.1) | (q[1], q[2])
    ops.MeasureFock() | q

import xcc
from strawberryfields import RemoteEngine
xcc.Settings(REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwYTdjOGE5Yi1lMzdkLTQ0MzItOTU2OC0xNzI3YzEwNmYyMzEifQ.eyJpYXQiOjE2NTg2MTU5MzUsImp0aSI6IjE5NDNmYTU5LWYxZmMtNDczZS04ZDliLThjZGE2MGVmOGE5MyIsImlzcyI6Imh0dHBzOi8vcGxhdGZvcm0ueGFuYWR1LmFpL2F1dGgvcmVhbG1zL3BsYXRmb3JtIiwiYXVkIjoiaHR0cHM6Ly9wbGF0Zm9ybS54YW5hZHUuYWkvYXV0aC9yZWFsbXMvcGxhdGZvcm0iLCJzdWIiOiJmMmIwYmJkYi05NzJkLTRiZDgtYjZhOS0xNTU3MWY4NDVlNjMiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoicHVibGljIiwic2Vzc2lvbl9zdGF0ZSI6ImIyNTI4ZmZlLTUwNzUtNDMwYy05YWZkLTdiZDA0MmI1ZTEwYyIsInNjb3BlIjoicHVibGljLXJvbGVzIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJzaWQiOiJiMjUyOGZmZS01MDc1LTQzMGMtOWFmZC03YmQwNDJiNWUxMGMifQ.c0wXKPXBCqfB9hOoFCe7-Fp-oSJ8wY2Sa_Sgvmn4-Oc").save()
import xcc.commands
xcc.commands.ping()

#eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwYTdjOGE5Yi1lMzdkLTQ0MzItOTU2OC0xNzI3YzEwNmYyMzEifQ.eyJpYXQiOjE2NTg2MTU5MzUsImp0aSI6IjE5NDNmYTU5LWYxZmMtNDczZS04ZDliLThjZGE2MGVmOGE5MyIsImlzcyI6Imh0dHBzOi8vcGxhdGZvcm0ueGFuYWR1LmFpL2F1dGgvcmVhbG1zL3BsYXRmb3JtIiwiYXVkIjoiaHR0cHM6Ly9wbGF0Zm9ybS54YW5hZHUuYWkvYXV0aC9yZWFsbXMvcGxhdGZvcm0iLCJzdWIiOiJmMmIwYmJkYi05NzJkLTRiZDgtYjZhOS0xNTU3MWY4NDVlNjMiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoicHVibGljIiwic2Vzc2lvbl9zdGF0ZSI6ImIyNTI4ZmZlLTUwNzUtNDMwYy05YWZkLTdiZDA0MmI1ZTEwYyIsInNjb3BlIjoicHVibGljLXJvbGVzIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJzaWQiOiJiMjUyOGZmZS01MDc1LTQzMGMtOWFmZC03YmQwNDJiNWUxMGMifQ.c0wXKPXBCqfB9hOoFCe7-Fp-oSJ8wY2Sa_Sgvmn4-Oc
eng = RemoteEngine("simulon_gaussian")
results = eng.run(prog, shots=100)

result = {}
for entry in results.samples:
    s = ""
    for item in entry:
        s += str(item) + ","
    if(s[:len(s)-1] not in result):
        result[s[:len(s)-1]] = 1
    else:
        result[s[:len(s)-1]] += 1
fig = plt.figure(figsize = (20, 5))
plt.bar(result.keys(), result.values(), 1, color='b')
plt.xlabel("Fock Measurement State (binary representation for 'qubit' analysis")
plt.ylabel("Occurences")
plt.show()