from PIL import Image
import streamlit as st
import services.supabase_client as supabase_client

im = Image.open("images/favicon.png")
st.set_page_config(
    page_title="Palavra Mestra",
    page_icon=im,
)

supabase = supabase_client.get_supabase_connection()

# Inicialização das variáveis de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# Função para logar o usuário
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state.logged_in = True
        st.session_state.role = 'admin'
        return True
    except Exception as e:
        st.error(f"Erro no login: {str(e)}")
        return False

def logout_user():
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# Interface de login
def login_page():
    st.title("Entrar")  
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")     
        if submit:
            if login_user(email, password):
                st.success("Login realizado com sucesso!")
                st.rerun()

# Interface principal após o login
def main_page():
    role = st.session_state.role
    dashboard = st.Page(
        "views/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=(role == "admin"),
    )
    # avaliacao = st.Page(
    #     "views/avaliacao.py",
    #     title="Avaliação de Redação",
    #     icon=":material/description:",
    # )
    pre_processamento = st.Page(
        "views/pre_processamento.py",
        title="Protótipo de Pre-processamento",
        icon=":material/description:",
    )
    settings = st.Page("services/settings.py", title="Configuração", icon=":material/settings:")
    logout_page = st.Page(logout_user, title="Sair", icon=":material/logout:")

    user_pages = [dashboard, pre_processamento]
    #admin_pages = [admin]
    account_pages = [settings, logout_page]

    st.logo("images/logo_palavra.png")

    page_dict = {}
    if st.session_state.role in ["integ", "admin"]:
        page_dict["Menu"] = user_pages

    if len(page_dict) > 0:
        pg = st.navigation(page_dict | {"Conta": account_pages})
    else:
        pg = st.navigation([st.Page(login_page)])

    pg.run()

# Fluxo principal da aplicação
if st.session_state.logged_in:
    main_page()
else:
    login_page()