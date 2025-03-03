from repositories.data_repository import DataRepository
import pandas as pd
from sklearn.cluster import KMeans
import openai
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

class DataService:
    """Service layer handling business logic for data operations"""
    
    def __init__(self, data_repository: DataRepository):
        self.data_repository = data_repository
        
        # Configurar OpenAI API (se disponível)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai.api_key = openai_key
            self.use_openai = True
        else:
            self.use_openai = False
            
        # Baixar recursos do NLTK para análise de texto
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
        
    def get_products(self, page=1, limit=10):
        """Get paginated products with basic analytics"""
        products = self.data_repository.fetch_products(page, limit)
        return {
            "data": products,
            "page": page,
            "limit": limit,
            "total": self.data_repository.count_products()
        }
        
    def get_product_details(self, product_id):
        """Get detailed information and analytics for a product"""
        product = self.data_repository.fetch_product(product_id)
        if not product:
            return None
            
        # Enrich with sales data
        sales_data = self.data_repository.fetch_product_sales(product_id)
        product["sales_data"] = sales_data
        
        # Add inventory predictions
        product["inventory_prediction"] = self._predict_inventory_needs(product_id, sales_data)
        
        # Extract key terms from description
        product["key_terms"] = self._extract_key_terms(product["description"])
        
        return product
        
    def generate_insights(self, product_type=None):
        """Generate AI insights based on product data"""
        products = self.data_repository.fetch_products_by_type(product_type) if product_type else self.data_repository.fetch_all_products(limit=1000)
        
        # Basic analytics insights
        if not products:
            return {"insights": ["No products found for analysis"], "metrics": {}}
            
        # Extract product lengths
        product_lengths = [p.get("product_length", 0) for p in products if p.get("product_length")]
        avg_length = sum(product_lengths) / len(product_lengths) if product_lengths else 0
        
        # Extract common words from titles
        all_titles = " ".join([p.get("title", "") for p in products if p.get("title")])
        common_words = self._extract_key_terms(all_titles, top_n=10)
        
        # Generate insights
        if self.use_openai:
            insights = self._generate_openai_insights(products)
        else:
            # Fallback to basic insights if OpenAI not available
            insights = [
                f"Average product length is {avg_length:.2f}",
                f"Most common terms in product titles: {', '.join(common_words)}",
                "Products with longer descriptions tend to have higher sales",
                "Consider optimizing product titles with popular keywords",
                "Short product titles with clear descriptions perform better"
            ]
        
        return {
            "insights": insights,
            "metrics": {
                "avg_length": avg_length,
                "common_terms": common_words,
                "product_count": len(products)
            }
        }
        
    def get_sales_metrics(self, period='month'):
        """Get time-based sales metrics for visualization"""
        raw_data = self.data_repository.fetch_sales_by_period(period)
        
        # Calculate total sales
        total_sales = sum(item['sales'] for item in raw_data)
        total_units = sum(item['units_sold'] for item in raw_data)
        
        # Get top products
        top_products = self.data_repository.fetch_top_products(limit=5)
        
        return {
            "time_series": raw_data,
            "top_products": top_products,
            "total_sales": total_sales,
            "total_units": total_units,
            "period": period
        }
        
    def get_top_products(self, limit=10):
        """Get top selling products"""
        return self.data_repository.fetch_top_products(limit)
        
    def get_product_types_distribution(self):
        """Get product types distribution"""
        return self.data_repository.get_product_types_distribution()
        
    def _predict_inventory_needs(self, product_id, sales_data):
        """Private method to predict inventory needs based on historical data"""
        if not sales_data:
            return {
                "recommended_stock": 50,
                "reorder_point": 20,
                "confidence": 0.5
            }
            
        # Calcular média de vendas diárias
        total_units = sum(sale.get('quantity', 0) for sale in sales_data)
        avg_daily_sales = total_units / 30  # Assumindo que os dados são de 30 dias
        
        # Calcular estoque recomendado (30 dias de vendas)
        recommended_stock = int(avg_daily_sales * 30)
        
        # Calcular ponto de reabastecimento (7 dias de vendas)
        reorder_point = int(avg_daily_sales * 7)
        
        # Calcular confiança com base no volume de dados
        confidence = min(0.5 + (len(sales_data) / 100), 0.95)
        
        return {
            "recommended_stock": recommended_stock,
            "reorder_point": reorder_point,
            "confidence": round(confidence, 2)
        }
        
    def _extract_key_terms(self, text, top_n=5):
        """Extract key terms from text"""
        if not text:
            return []
            
        try:
            # Tokenizar e remover stopwords
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words and len(w) > 2]
            
            # Contar frequência
            word_freq = Counter(filtered_tokens)
            
            # Retornar os termos mais comuns
            return [word for word, freq in word_freq.most_common(top_n)]
        except:
            # Fallback em caso de erro
            return []
            
    def _generate_openai_insights(self, products):
        """Generate insights using OpenAI API"""
        try:
            # Preparar dados para o prompt
            sample_products = products[:5]  # Usar amostra para economizar tokens
            products_text = "\n".join([
                f"Product: {p.get('title', 'Unknown')}, Type: {p.get('product_type_id', 'Unknown')}, Length: {p.get('product_length', 'Unknown')}"
                for p in sample_products
            ])
            
            prompt = f"""
            Analyze these e-commerce products and provide 5 actionable business insights:
            {products_text}
            
            Provide 5 short, specific insights that would help optimize product listings and sales.
            """
            
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            # Processar resposta
            insights_text = response.choices[0].text.strip()
            insights = [line.strip() for line in insights_text.split("\n") if line.strip()]
            
            # Limitar a 5 insights
            return insights[:5]
            
        except Exception as e:
            print(f"Error generating OpenAI insights: {e}")
            # Fallback para insights básicos
            return [
                "Optimize product descriptions with more details",
                "Consider adding more products in underrepresented categories",
                "Products with clearer titles tend to perform better",
                "Consider bundling related products to increase average order value",
                "Regularly update product information to maintain relevance"
            ]