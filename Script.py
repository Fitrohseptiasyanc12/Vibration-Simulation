import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from scipy.integrate import solve_ivp
from matplotlib.lines import Line2D
from PIL import Image
import os

# Path untuk folder assets
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, "assets")

logo_path = os.path.join(assets_dir, "logo.JPG")
profile_path = os.path.join(assets_dir, "profile.JPG")

# Cek apakah file ada sebelum dibuka
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
else:
    logo = None
    st.error("Gambar logo tidak ditemukan! Pastikan 'logo.JPG' ada di folder assets.")

if os.path.exists(profile_path):
    profile = Image.open(profile_path)
else:
    profile = None
    st.error("Gambar profile tidak ditemukan! Pastikan 'profile.JPG' ada di folder assets.")

# Sidebar Navigation
st.sidebar.header("Pilih Menu")
page = st.sidebar.radio("Navigation", ["Home", "My Profile", "VibSim"])

if page == "Home":
    if logo:
        st.image(logo, width=200)
    st.write("President University")
    st.title("WELCOME TO VIBSIM")
    st.subheader("Mechanical Vibration")
    st.write("Vibration Simulation (VibSim) dirancang untuk membantu anda dalam mensimulasikan sistem pegas-massa-redaman secara interaktif")
    st.write("Silahkan pilih menu di kiri atas untuk memulai.")

elif page == "My Profile":
    if profile:
        st.image(profile, width=200)
    st.header("My Profile")
    st.write("Nama: Fitroh Septiasya Nour Cahya")
    st.write("Email: fitroh.cahya@student.president.ac.id")
    st.write("Domisili: Cikarang Barat")

elif page == "VibSim":
    # Fungsi untuk menyelesaikan persamaan diferensial sistem pegas-massa-redaman
    def mass_spring_damper(t, y, m, k, c):
        x, v = y
        dxdt = v
        dvdt = (-k*x - c*v) / m
        return [dxdt, dvdt]

    # Fungsi untuk mensimulasikan sistem dan menampilkan grafik
    def simulate(m, k, c, x0, v0, t_end):
        t_span = (0, t_end)
        t_eval = np.linspace(0, t_end, 1000)

        # Simulasi sistem dengan redaman
        sol = solve_ivp(mass_spring_damper, t_span, [x0, v0], t_eval=t_eval, args=(m, k, c))

        # Simulasi sistem tanpa redaman
        sol_undamped = solve_ivp(mass_spring_damper, t_span, [x0, v0], t_eval=t_eval, args=(m, k, 0))

        # Perhitungan parameter sistem
        omega_n = np.sqrt(k / m)  # Frekuensi natural
        zeta = c / (2 * np.sqrt(k * m))  # Rasio redaman
        omega_d = omega_n * np.sqrt(1 - zeta**2) if zeta < 1 else 0  # Frekuensi teredam
        gaya_pegas = k * x0  # Gaya pegas (F = kx)
        
        # Grafik respons sistem
        fig, ax = plt.subplots()
        ax.plot(sol.t, sol.y[0], color='blue')
        ax.plot(sol_undamped.t, sol_undamped.y[0], color='green', linestyle='dashed')

        # Buat legenda kustom
        legend_elements = [
            Line2D([0], [0], color="green", lw=2, linestyle="dashed", label="Undamped"),
            Line2D([0], [0], color="blue", lw=2, label="Damped")
        ]

        # Posisikan legenda di atas grafik
        ax.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, 1.2), ncol=2, frameon=True)

        # Atur sumbu X mulai dari angka 1, 2, 3, ...
        ax.set_xticks(np.arange(1, t_end + 1, 1))
        ax.set_xlabel("Waktu (s)")
        ax.set_ylabel("Amplitudo")
        ax.grid()

        return fig, omega_n, zeta, omega_d, gaya_pegas

    # Antarmuka Streamlit
    st.title("Vibration Simulation Tool")
    st.sidebar.header("Input Parameter")

    m = st.sidebar.number_input("Massa (m)", min_value=0.1, value=1.0, step=0.1)
    k = st.sidebar.number_input("Konstanta Pegas (k)", min_value=1, value=100, step=1)
    c = st.sidebar.number_input("Konstanta Redaman (C)", min_value=0, value=5, step=1)
    x0 = st.sidebar.number_input("Posisi Awal (X Awal)", value=0.1, step=0.01)
    v0 = st.sidebar.number_input("Kecepatan Awal (v)", value=0.1, step=0.01) 
    t_end = st.sidebar.slider("Durasi Simulasi (s)", min_value=1, max_value=20, value=10)

    # Keterangan Parameter di sidebar
    st.sidebar.markdown("### Keterangan Parameter")
    st.sidebar.markdown("- **Massa (m)**: Besar massa benda dalam kg")
    st.sidebar.markdown("- **Konstanta Pegas (k)**: Kekakuan pegas dalam N/m")
    st.sidebar.markdown("- **Konstanta Redaman (C)**: Koefisien redaman dalam Ns/m")
    st.sidebar.markdown("- **Posisi Awal (X Awal)**: Posisi awal benda dalam meter")
    st.sidebar.markdown("- **Kecepatan Awal (v)**: Kecepatan awal benda dalam m/s")
    st.sidebar.markdown("- **Durasi Simulasi**: Waktu total simulasi dalam detik")

    # Tombol simulasi
    if st.sidebar.button("Simulate"):
        fig, omega_n, zeta, omega_d, gaya_pegas = simulate(m, k, c, x0, v0, t_end)

        # Tampilkan hasil simulasi
        st.pyplot(fig)

        # Hasil Perhitungan
        st.markdown("## Hasil Perhitungan")
        st.latex(r"\text{Natural Frequency } (\omega_n) = " + f"{omega_n:.3f}" + r" \text{ rad/s}")
        st.latex(r"\text{Damping Ratio } (\zeta) = " + f"{zeta:.3f}")
        if zeta < 1:
            st.latex(r"\text{Damped Frequency } (\omega_d) = " + f"{omega_d:.3f}" + r" \text{ rad/s}")
        else:
            st.markdown("**Overdamped system (no oscillation)**")
        st.latex(r"\text{Gaya Pegas } (F) = " + f"{gaya_pegas:.3f}" + r" \text{ N}")
