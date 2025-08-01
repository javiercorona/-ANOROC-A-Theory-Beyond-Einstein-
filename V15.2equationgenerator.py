import sympy as sp
import streamlit as st
from typing import Dict, List, Callable

class ANOROCEquationBuilder:
    def __init__(self):
        # Initialize symbols and base terms
        self.mu, self.nu = sp.symbols('\\mu \\nu')
        self.K = sp.Symbol('K')
        self.K_tot = sp.Symbol('K_{tot}')
        self.phi = sp.Function('\\phi')(sp.Symbol('x'))
        self.base_terms = {
            'G': sp.Function('G')(self.mu, self.nu),
            'H': sp.Function('H')(self.mu, self.nu),
            'V_string': sp.Function('V')**(sp.Symbol('(string)'))(self.mu, self.nu),
            'Q': sp.Function('Q')(self.mu, self.nu),
            'T_eff': sp.Function('T')**(sp.Symbol('(eff)'))(self.mu, self.nu)
        }
        self.custom_terms = {}
        self.equation_parts = []
        
    def add_term(self, term: sp.Expr, description: str):
        """Add a term to the equation with metadata."""
        self.equation_parts.append({
            'term': term,
            'description': description,
            'latex': sp.latex(term)
        })
    
    def build_equation(self) -> sp.Eq:
        """Construct the full equation from added terms."""
        lhs = sum([part['term'] for part in self.equation_parts if not part['is_rhs']])
        rhs = sum([part['term'] for part in self.equation_parts if part['is_rhs']])
        return sp.Eq(lhs, rhs)
    
    def add_custom_term(self, name: str, term_func: Callable, params: Dict):
        """Register a user-defined term template."""
        self.custom_terms[name] = {
            'func': term_func,
            'params': params
        }

# Predefined term templates
def cutoff_term(K, K_tot, G):
    return (1 - sp.exp(-K/K_tot)) * G

def string_correction(g_z, l_5, V):
    return g_z**2 * l_5**2 * V

# Streamlit UI
def main():
    st.title("ANOROC-String Equation Playground")
    builder = ANOROCEquationBuilder()
    
    # Sidebar for term selection
    st.sidebar.header("Add Terms")
    term_type = st.sidebar.selectbox(
        "Term Type", 
        ["Cutoff", "String Correction", "Quantum", "Custom"]
    )
    
    # Add terms based on selection
    if term_type == "Cutoff":
        K_val = st.sidebar.slider("K/K_tot ratio", 0.1, 10.0, 1.0)
        term = cutoff_term(builder.K, builder.K_tot, builder.base_terms['G'])
        builder.add_term(term, f"Cutoff term with K/K_tot={K_val}")
        
    elif term_type == "String Correction":
        g_z = st.sidebar.slider("g_z", 0.1, 2.0, 1.0)
        l_5 = st.sidebar.slider("l_5", 0.1, 5.0, 1.0)
        term = string_correction(g_z, l_5, builder.base_terms['V_string'])
        builder.add_term(term, f"String correction (g_z={g_z}, l_5={l_5})")
    
    elif term_type == "Custom":
        custom_name = st.sidebar.text_input("Term Name (e.g., 'Dark_flux')")
        if st.sidebar.button("Register Custom Term"):
            # Example: Let users define terms via lambda
            custom_func = lambda params: params['a'] * builder.base_terms['G']
            builder.add_custom_term(custom_name, custom_func, {'a': 1.0})
    
    # Main display
    st.header("Current Equation")
    eq = builder.build_equation()
    st.latex(sp.latex(eq))
    
    st.header("Term Descriptions")
    for part in builder.equation_parts:
        st.markdown(f"- **{part['description']}**: `${part['latex']}`")
    
    # Export options
    if st.button("Export to LaTeX"):
        st.code(sp.latex(eq), language='latex')

if __name__ == "__main__":
    main()
