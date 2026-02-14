"""
Statistical Analysis Module
통계 분석 모듈

Includes:
- Probability distribution fitting (DE, N, NN, NDE, DDE)
- Maximum Likelihood Estimation (MLE)
- Data fitting and model selection
"""

import numpy as np
from scipy import stats, optimize
from typing import Dict, Tuple, Callable, Optional
import warnings


class DistributionFitter:
    """
    Fit probability distributions to observed lateral deviation data
    관측된 횡적 편차 데이터에 확률 분포 피팅
    """
    
    def __init__(self, data: np.ndarray):
        """
        Initialize with observed data
        
        Parameters:
        -----------
        data : np.ndarray
            Observed lateral deviations (nm)
        """
        self.data = data
        self.fitted_params = {}
        self.log_likelihoods = {}
        
    def fit_double_exponential(self) -> Tuple[Dict, float]:
        """
        Fit Double Exponential (Laplace) distribution
        이중지수분포 피팅
        
        PDF: f(x) = (1 / 2b) * exp(-|x - μ| / b)
        
        Returns:
        --------
        tuple : (parameters dict, log-likelihood)
        """
        # MLE for Double Exponential
        mu = np.median(self.data)
        b = np.mean(np.abs(self.data - mu))
        
        # Calculate log-likelihood
        log_likelihood = -len(self.data) * np.log(2 * b) - np.sum(np.abs(self.data - mu)) / b
        
        params = {'mu': mu, 'b': b}
        self.fitted_params['DE'] = params
        self.log_likelihoods['DE'] = log_likelihood
        
        return params, log_likelihood
    
    def fit_gaussian(self) -> Tuple[Dict, float]:
        """
        Fit Gaussian (Normal) distribution
        가우스분포 피팅
        
        PDF: f(x) = (1 / √(2πσ²)) * exp(-(x - μ)² / 2σ²)
        
        Returns:
        --------
        tuple : (parameters dict, log-likelihood)
        """
        mu = np.mean(self.data)
        sigma = np.std(self.data, ddof=1)
        
        # Calculate log-likelihood
        log_likelihood = -0.5 * len(self.data) * np.log(2 * np.pi * sigma**2) - \
                         np.sum((self.data - mu)**2) / (2 * sigma**2)
        
        params = {'mu': mu, 'sigma': sigma}
        self.fitted_params['N'] = params
        self.log_likelihoods['N'] = log_likelihood
        
        return params, log_likelihood
    
    def fit_mixture_gaussian(self, n_components: int = 2) -> Tuple[Dict, float]:
        """
        Fit Mixture of Gaussians distribution
        혼합 가우스분포 피팅
        
        PDF: f(x) = Σ wi * N(x | μi, σi²)
        
        Parameters:
        -----------
        n_components : int
            Number of Gaussian components (default: 2)
        
        Returns:
        --------
        tuple : (parameters dict, log-likelihood)
        """
        from sklearn.mixture import GaussianMixture
        
        data_reshaped = self.data.reshape(-1, 1)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gmm = GaussianMixture(n_components=n_components, random_state=42)
            gmm.fit(data_reshaped)
        
        log_likelihood = gmm.score(data_reshaped) * len(self.data)
        
        params = {
            'weights': gmm.weights_,
            'means': gmm.means_.flatten(),
            'covariances': np.sqrt(gmm.covariances_).flatten()
        }
        
        self.fitted_params['NN'] = params
        self.log_likelihoods['NN'] = log_likelihood
        
        return params, log_likelihood
    
    def fit_mixture_double_exponential(self, n_components: int = 2) -> Tuple[Dict, float]:
        """
        Fit Mixture of Double Exponential distributions
        혼합 이중지수분포 피팅
        
        PDF: f(x) = Σ wi * DE(x | μi, bi)
        
        Parameters:
        -----------
        n_components : int
            Number of components (default: 2)
        
        Returns:
        --------
        tuple : (parameters dict, log-likelihood)
        """
        # Initialize with k-means clustering
        from sklearn.cluster import KMeans
        
        data_reshaped = self.data.reshape(-1, 1)
        kmeans = KMeans(n_clusters=n_components, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data_reshaped)
        
        weights = []
        mus = []
        bs = []
        
        for i in range(n_components):
            cluster_data = self.data[labels == i]
            if len(cluster_data) > 0:
                weight = len(cluster_data) / len(self.data)
                mu = np.median(cluster_data)
                b = np.mean(np.abs(cluster_data - mu))
                
                weights.append(weight)
                mus.append(mu)
                bs.append(b)
        
        # Ensure weights sum to 1
        weights = np.array(weights) / np.sum(weights)
        
        # Calculate log-likelihood
        log_likelihood = 0
        for x in self.data:
            prob = 0
            for w, mu, b in zip(weights, mus, bs):
                prob += w * (1 / (2 * b)) * np.exp(-np.abs(x - mu) / b)
            log_likelihood += np.log(prob + 1e-10)
        
        params = {
            'weights': weights,
            'mus': np.array(mus),
            'bs': np.array(bs)
        }
        
        self.fitted_params['DDE'] = params
        self.log_likelihoods['DDE'] = log_likelihood
        
        return params, log_likelihood
    
    def fit_gaussian_double_exponential_mixture(self) -> Tuple[Dict, float]:
        """
        Fit mixture of Gaussian and Double Exponential
        가우스-이중지수 혼합분포 피팅
        
        PDF: f(x) = w1 * N(x | μ1, σ1²) + w2 * DE(x | μ2, b2)
        
        Returns:
        --------
        tuple : (parameters dict, log-likelihood)
        """
        # Split data for initialization
        n = len(self.data)
        n_half = n // 2
        
        # Gaussian component
        data1 = self.data[:n_half]
        mu1 = np.mean(data1)
        sigma1 = np.std(data1, ddof=1)
        
        # Double Exponential component
        data2 = self.data[n_half:]
        mu2 = np.median(data2)
        b2 = np.mean(np.abs(data2 - mu2))
        
        w1 = 0.5
        w2 = 0.5
        
        # Calculate log-likelihood
        log_likelihood = 0
        for x in self.data:
            prob = w1 * stats.norm.pdf(x, mu1, sigma1) + \
                   w2 * stats.laplace.pdf(x, mu2, b2)
            log_likelihood += np.log(prob + 1e-10)
        
        params = {
            'w1': w1, 'mu1': mu1, 'sigma1': sigma1,
            'w2': w2, 'mu2': mu2, 'b2': b2
        }
        
        self.fitted_params['NDE'] = params
        self.log_likelihoods['NDE'] = log_likelihood
        
        return params, log_likelihood
    
    def fit_all_distributions(self) -> Dict[str, Tuple[Dict, float]]:
        """
        Fit all distribution models and compare
        
        Returns:
        --------
        dict : Dictionary with model names as keys and (params, log_likelihood) as values
        """
        results = {}
        
        # Fit each distribution
        results['DE'] = self.fit_double_exponential()
        results['N'] = self.fit_gaussian()
        results['NN'] = self.fit_mixture_gaussian()
        results['DDE'] = self.fit_mixture_double_exponential()
        results['NDE'] = self.fit_gaussian_double_exponential_mixture()
        
        return results
    
    def select_best_model(self, criterion: str = 'log_likelihood') -> str:
        """
        Select best distribution model
        
        Parameters:
        -----------
        criterion : str
            Selection criterion ('log_likelihood', 'aic', 'bic')
        
        Returns:
        --------
        str : Best model name
        """
        if not self.log_likelihoods:
            self.fit_all_distributions()
        
        if criterion == 'log_likelihood':
            best_model = max(self.log_likelihoods, key=self.log_likelihoods.get)
        else:
            # Implement AIC/BIC if needed
            best_model = max(self.log_likelihoods, key=self.log_likelihoods.get)
        
        return best_model
    
    def fit_distribution(self, model: str = 'DDE') -> Callable:
        """
        Get PDF function for specified distribution model
        
        Parameters:
        -----------
        model : str
            Distribution model ('DE', 'N', 'NN', 'DDE', 'NDE')
        
        Returns:
        --------
        callable : PDF function
        """
        if model not in self.fitted_params:
            if model == 'DE':
                self.fit_double_exponential()
            elif model == 'N':
                self.fit_gaussian()
            elif model == 'NN':
                self.fit_mixture_gaussian()
            elif model == 'DDE':
                self.fit_mixture_double_exponential()
            elif model == 'NDE':
                self.fit_gaussian_double_exponential_mixture()
        
        params = self.fitted_params[model]
        
        if model == 'DE':
            return lambda x: stats.laplace.pdf(x, params['mu'], params['b'])
        elif model == 'N':
            return lambda x: stats.norm.pdf(x, params['mu'], params['sigma'])
        elif model == 'NN':
            def mixture_gaussian_pdf(x):
                result = 0
                for w, mu, sigma in zip(params['weights'], params['means'], params['covariances']):
                    result += w * stats.norm.pdf(x, mu, sigma)
                return result
            return mixture_gaussian_pdf
        elif model == 'DDE':
            def mixture_de_pdf(x):
                result = 0
                for w, mu, b in zip(params['weights'], params['mus'], params['bs']):
                    result += w * stats.laplace.pdf(x, mu, b)
                return result
            return mixture_de_pdf
        elif model == 'NDE':
            return lambda x: (params['w1'] * stats.norm.pdf(x, params['mu1'], params['sigma1']) +
                            params['w2'] * stats.laplace.pdf(x, params['mu2'], params['b2']))
        
        # Default to Gaussian
        return lambda x: stats.norm.pdf(x, np.mean(self.data), np.std(self.data))


class DataAnalyzer:
    """
    Analyze flight trajectory data
    비행 궤적 데이터 분석
    """
    
    @staticmethod
    def calculate_lateral_deviations(
        trajectories: np.ndarray,
        route_centerline: np.ndarray
    ) -> np.ndarray:
        """
        Calculate lateral deviations from route centerline
        
        Parameters:
        -----------
        trajectories : np.ndarray
            Array of trajectory points (N, 2) - [lon, lat]
        route_centerline : np.ndarray
            Array of route centerline points (M, 2) - [lon, lat]
        
        Returns:
        --------
        np.ndarray : Lateral deviations in nautical miles
        """
        # Calculate perpendicular distance from each point to centerline
        # Using Haversine formula for great circle distance
        
        deviations = []
        for point in trajectories:
            min_distance = float('inf')
            for i in range(len(route_centerline) - 1):
                distance = DataAnalyzer._point_to_line_distance(
                    point, route_centerline[i], route_centerline[i + 1]
                )
                min_distance = min(min_distance, distance)
            deviations.append(min_distance)
        
        return np.array(deviations)
    
    @staticmethod
    def _point_to_line_distance(
        point: np.ndarray,
        line_start: np.ndarray,
        line_end: np.ndarray
    ) -> float:
        """
        Calculate perpendicular distance from point to line segment
        
        Parameters:
        -----------
        point : np.ndarray
            Point coordinates [lon, lat]
        line_start : np.ndarray
            Line start coordinates [lon, lat]
        line_end : np.ndarray
            Line end coordinates [lon, lat]
        
        Returns:
        --------
        float : Distance in nautical miles
        """
        # Simplified calculation using cross-track distance
        # For more accurate calculation, use Haversine formula
        
        # Convert to radians
        lat1, lon1 = np.radians(line_start[1]), np.radians(line_start[0])
        lat2, lon2 = np.radians(line_end[1]), np.radians(line_end[0])
        lat3, lon3 = np.radians(point[1]), np.radians(point[0])
        
        # Cross-track distance
        delta13 = np.arccos(np.sin(lat1) * np.sin(lat3) + 
                           np.cos(lat1) * np.cos(lat3) * np.cos(lon3 - lon1))
        
        theta13 = np.arctan2(np.sin(lon3 - lon1) * np.cos(lat3),
                            np.cos(lat1) * np.sin(lat3) - 
                            np.sin(lat1) * np.cos(lat3) * np.cos(lon3 - lon1))
        
        theta12 = np.arctan2(np.sin(lon2 - lon1) * np.cos(lat2),
                            np.cos(lat1) * np.sin(lat2) - 
                            np.sin(lat1) * np.cos(lat2) * np.cos(lon2 - lon1))
        
        dxt = np.arcsin(np.sin(delta13) * np.sin(theta13 - theta12))
        
        # Convert to nautical miles (1 radian on Earth = 3440 nm)
        return abs(dxt * 3440.08)
    
    @staticmethod
    def extract_waypoint_crossing_times(
        trajectories: list,
        waypoint: Tuple[float, float],
        tolerance_nm: float = 5.0
    ) -> np.ndarray:
        """
        Extract times when aircraft cross a waypoint
        
        Parameters:
        -----------
        trajectories : list
            List of trajectory dictionaries with 'time', 'lat', 'lon'
        waypoint : tuple
            Waypoint coordinates (lon, lat)
        tolerance_nm : float
            Tolerance for waypoint crossing detection (nm)
        
        Returns:
        --------
        np.ndarray : Array of crossing times (timestamps)
        """
        crossing_times = []
        
        for trajectory in trajectories:
            for i in range(len(trajectory['time'])):
                point = np.array([trajectory['lon'][i], trajectory['lat'][i]])
                waypoint_arr = np.array(waypoint)
                
                # Calculate distance to waypoint
                distance = DataAnalyzer._haversine_distance(point, waypoint_arr)
                
                if distance <= tolerance_nm:
                    crossing_times.append(trajectory['time'][i])
                    break
        
        return np.array(crossing_times)
    
    @staticmethod
    def _haversine_distance(point1: np.ndarray, point2: np.ndarray) -> float:
        """
        Calculate Haversine distance between two points
        
        Parameters:
        -----------
        point1 : np.ndarray
            [lon, lat] in degrees
        point2 : np.ndarray
            [lon, lat] in degrees
        
        Returns:
        --------
        float : Distance in nautical miles
        """
        lon1, lat1 = np.radians(point1)
        lon2, lat2 = np.radians(point2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Earth radius in nautical miles
        r = 3440.08
        
        return c * r
