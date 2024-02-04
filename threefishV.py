import time
import os

R = [[14, 16],
     [52, 57],
     [23, 40],
     [5, 37],
     [25, 33],
     [46, 12],
     [58, 22],
     [32, 32]]

max_int = 2 ** 64

C = 0x1BD11BDAA9FC1A22
Nw = 4
Nr = 72
pi = [0,3,2,1]

def MIX(x_0, x_1, d, j):
    y_0 = (x_0 + x_1) % max_int
    y_1 = (((x_1 << R[d % 8][j]) % (1 << 64)) | (x_1 >> (64 - R[d % 8][j]))) ^ y_0
    return y_0, y_1


key = 'key of 32,64 or 128 bytes length'
tweak = 'tweak: 16 bytes '

key_bytes = bytearray(key, 'utf-8')
tweak_bytes = bytearray(tweak, 'utf-8')


file = open('./testV.txt', 'rb')
file_encrypt = open('./test_encrypt_result.txt', 'w')
file_decrypt = open('./test_decrypt.txt', 'w')

start_time = time.time()

plaintext_bytes = bytearray(file.read())
length_text = len(plaintext_bytes)
print(length_text)
block_length = 32
padding = block_length - (length_text % block_length)
print(padding)
if padding == 1:
    plaintext_bytes.append(0x80)
elif padding > 1 and padding < 32:
    plaintext_bytes.append(0x80)
    for i in range(0, padding - 1):
        plaintext_bytes.append(0x00)
print(length_text)
print(plaintext_bytes)

K = [0,0,0,0,0]
i = 0
for word in range(Nw):
    K[word] = int.from_bytes(key_bytes[i:i+8], 'little', signed=False)
    i += 8
    
T = [0,0,0]
j = 0
for word in range(2):
    T[word] = int.from_bytes(tweak_bytes[j:j+8], 'little', signed=False)
    j += 8

for i in range(2):
    T[2] ^= T[i]
print(f"T = {T}")

K[4] = C
for i in range(Nw):
    K[4] ^= K[i]
print(f"K = {K}")




Ks = []
for i in range((Nr//4)+1):
    Ks.append([0,0,0,0])    

for s in range((Nr//4)+1):
    for i in range(Nw):
        if i == 0:
            Ks[s][i] = K[(s + i) % 5]
        elif i == 1:
            Ks[s][i] = (K[(s + i) % 5] + T[s % 3]) % max_int
        elif i == 2:
            Ks[s][i] = (K[(s + i) % 5] + T[(s + 1) % 3]) % max_int
        elif i == 3:
            #print(f"(K[({s} + {i}) % {5}] + {s}) = {(K[(s + i) % 5] + s) }")
            Ks[s][i] = (K[(s + i) % 5] + s) % max_int
    print(f"Ks[{s}] = {Ks[s]}")
c = []

###encrypt###

i = 0
while i < length_text:
    P = [0,0,0,0]

    for word in range(Nw):
        P[word] = int.from_bytes(plaintext_bytes[i:i+8], 'little', signed=False)
        i += 8
    
    v = []
    e = []
    f = []
    for j in range(Nr + 1):
        v.append([0,0,0,0])
        e.append([0,0,0,0])
        f.append([0,0,0,0])
   
    for j in range(Nw):
        v[0][j] = P[j]
    
    for d in range(Nr):
        for j in range(Nw):
            if d % 4 == 0:
                e[d][j] = (v[d][j] + Ks[d // 4][j]) % max_int
                print(f"Ks[{d//4}][{j}] = {Ks[d//4][j]}")
            else:
                e[d][j] = v[d][j]

        for j in range(2):
            f[d][2*j], f[d][(2*j)+1] = MIX(e[d][2*j], e[d][(2*j)+1], d, j)
    
        for j in range(Nw):
            v[d+1][j] = f[d][pi[j]]
    print("####")
    print(v[d+1])


    c = []
    for j in range(Nw):
        c.append((v[72][j] + Ks[72//4][j]) % max_int)
    print("C!!!!!!")  
    #print(c[0].to_bytes(8, 'big') + c[1].to_bytes(8, 'big') + c[2].to_bytes(8, 'big') + c[3].to_bytes(8, 'little'))
    print(c)
    print("C")
    


    file_encrypt.write(str(c[0].to_bytes(8, 'little') + c[1].to_bytes(8, 'little') + c[2].to_bytes(8, 'little') + c[3].to_bytes(8, 'little')))

    def deMIX(y_0, y_1, d, j):
        y_1 ^= y_0
        x_1 = ( ((y_1 << (64 - R[d % 8][j]))  % (1 << 64)) | ((y_1 >> R[d % 8][j])) )                     
        x_0 = (y_0 - x_1) % max_int
        return x_0, x_1

###decrypt###
    for k in range(Nw):
        v[72][k] = (c[k] - Ks[72//4][k]) % max_int

    for d in range(Nr, 0, -1):
        
        for j in range(Nw):
            f[d-1][pi[j]] = v[d][j]
    
        for j in range(2):
            e[d-1][2*j], e[d-1][(2*j)+1] = deMIX(f[d-1][2*j], f[d-1][(2*j)+1], d-1, j)
        
        for j in range(Nw):
            if (d-1) % 4 == 0:
                v[d-1][j] = (e[d-1][j] - Ks[(d-1) // 4][j]) % max_int
            else:
                v[d-1][j] = e[d-1][j]

        for j in range(Nw):
            P[j] = v[0][j]
    print(i)
    print(length_text)
    if i > length_text :
        index_P = 0
        index_D = 0
        print("yes")
        for num in range(3, -1, -1):
            D = P[num].to_bytes(8, 'little')
            print(D)
            for ind in range(7, -1, -1):
                if D[ind] == 0x80:
                    index_P = num
                    index_D = ind
                    break
        print(index_P)
        last = P[index_P].to_bytes(8, 'little')
        last = last[0:index_D]
        decrypt_block = bytes()
        for p in P[:index_P]:
            print(p.to_bytes(8,'little'))
            decrypt_block += p.to_bytes(8, 'little')
        decrypt_block += last
        print(last)
        file_decrypt.write(str(decrypt_block))
    else:
        print(P[0].to_bytes(8, 'little'))
        print(P[1].to_bytes(8, 'little'))
        print(P[2].to_bytes(8, 'little'))
        print(P[3].to_bytes(8, 'little'))
        file_decrypt.write(str(P[0].to_bytes(8, 'little') + P[1].to_bytes(8, 'little') + P[2].to_bytes(8, 'little') + P[3].to_bytes(8, 'little')))

end_time = time.time()
print(str(end_time - start_time) + ' seconds')
