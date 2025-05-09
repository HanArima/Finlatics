import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA

df = pd.read_csv("Facebook_Marketplace_data.csv")
df = df.drop('Column1', axis=1)
df = df.drop('Column2', axis=1)
df = df.drop('Column3', axis=1)
df = df.drop('Column4', axis=1)

df['status_published'] = pd.to_datetime(df['status_published'])
df['date'] = df['status_published'].dt.date
df['month'] = df['status_published'].dt.month
df['year'] = df['status_published'].dt.year
df['time'] = df['status_published'].dt.time
df['hour_of_day'] = df['status_published'].dt.hour

def main():

    ''' Before performing Scaling or Transformation on the Data'''
    #display_table(df)
    #relation_bw_reaction_timestamp(df)
    #correlation_matrix(df)
    
    ''' After performing scaling and transformation on the Data'''
    preprocessed_df = data_preprocessing(df)
    find_value_of_k_scaling(preprocessed_df)
    kmeansclustering(preprocessed_df)

def detect_and_count_outliers(df, threshold=1.5): # you can change the threshold

    outlier_counts = {}  # Store outlier counts for each column
    for col in df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        
        # Calculate number of outliers
        num_outliers = len(outliers)
        outlier_counts[col] = num_outliers

        # Calculate percentage of outliers
        percentage_outliers = (num_outliers / len(df)) * 100
        print(f"Column {col}: {percentage_outliers:.2f}% outliers")

    return outlier_counts

def data_preprocessing(df):
    print(df.shape)
    print(df.info())
    print(df.isnull().sum())
    print(df.describe())

    # ENCODING
    # Converting the status type to numeric for the model using One Hot Encoder
    encoder = OneHotEncoder()
    encoded_data = encoder.fit_transform(df[['status_type']])
    encoded_df = pd.DataFrame(encoded_data.toarray(), columns=encoder.get_feature_names_out())

    # SCALING AND TRANSFORMATION
    # Selecting features for scaling
    features = df.drop(['status_type','status_published', 'date', 'time', 'year', 'month', 'hour_of_day', 'status_id'], axis=1)
    # Apply log transformation: To handle the skewness of data
    features[['num_reactions', 'num_comments', 'num_shares', 'num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys']] = np.log1p(features[['num_reactions', 'num_comments', 'num_shares', 'num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys']])
    # Robust Scaling
    scaler = RobustScaler()
    scaled_features = scaler.fit_transform(features)
    # Transforming Scaled features to Data Frame
    scaled_df = pd.DataFrame(scaled_features, columns=features.columns)
    scaled_df = pd.concat([scaled_df, encoded_df], axis=1)


    ''' Stuff for outlier visualization '''
    # Create a list of features to be considered.
    features_considered = scaled_df[['num_reactions', 'num_comments' ,'num_shares' ,'num_likes' ,'num_loves' ,'num_wows' ,'num_hahas' ,'num_sads' ,'num_angrys']]
    # Melt the DataFrame into long format
    melted_df = features_considered.melt(var_name='Feature', value_name='Value')

    # Create the boxplot
    plt.figure(figsize=(100, 15)) # Adjust figure size as needed
    sns.violinplot(x='Feature', y='Value', data=melted_df, palette='muted')
    sns.boxplot(x='Feature', y='Value', data=melted_df, width=0.2)
    plt.title("Overlay of Boxplot and Violinplot for All Features")
    plt.xlabel("Features")
    plt.ylabel("Values")
    #plt.yscale('log')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45) # Rotate x-axis labels for better readability
    #plt.tight_layout()
    plt.show()

    '''Returning count of the outlier'''
    count = detect_and_count_outliers(scaled_df)
    print(count)

    return scaled_df
        
def avg():
    average_values = df.groupby('status_type')[['num_reactions', 'num_comments', 'num_shares']].mean()
    print(average_values)

def count_of_diff_post():

    plt.figure(figsize=(10,20))
    sns.countplot(df, x='status_type',)
    plt.xlabel("Type of Posts")
    plt.title("Count Plot for each type of Posts")
    plt.show()

def display_table(df):
    print(df.head(10))

def find_value_of_k_scaling(scaled_df):
    
    ''' Elbow Method '''
    wcss = []
    for i in range(1,11):
        kmean = KMeans(n_clusters=i, init="k-means++", random_state=42)
        kmean.fit(scaled_df)
        wcss.append(kmean.inertia_)
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=range(1, 11), y=wcss, marker='o')
    plt.title('Elbow Method')
    plt.xlabel('Number of Clusters')
    plt.ylabel('WCSS')
    plt.show()

    ''' Silhoutte Method '''
    silhoutte = []
    for i in range(2,11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_df)

        silhoutte_avg = silhouette_score(scaled_df, cluster_labels)
        silhoutte.append(silhoutte_avg)
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=range(2,11), y=silhoutte, marker='o')
    plt.title('Silhouette Method for Optimal k')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Silhouette Score')
    plt.show()

    ''' Davies-Bouldin Index '''
    dbi = []
    for i in range(2,11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_df)

        db_index = davies_bouldin_score(scaled_df, cluster_labels)
        dbi.append(db_index)
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=range(2,11), y=dbi, marker='o')
    plt.title('Davies-Bouldin Index Method for Optimal k')
    plt.xlabel('Number of Clusters') 
    plt.ylabel('Davies-Bouldin Index Score')
    plt.show()

def kmeansclustering(scaled_df):

    # Training Model
    ''' IN 2D '''

    for k in [2]:
        kmeans_model = KMeans(n_clusters=k, init='k-means++', random_state=53)
        
        # Perform PCA to reduce dimensions to 2
        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(scaled_df)
        
        y_kmeans = kmeans_model.fit_predict(pca_features)
        print(f"Silhoutte score for k value {k} is ", silhouette_score(pca_features, y_kmeans))
        print(f"DBI for k value {k} is ", davies_bouldin_score(pca_features, y_kmeans))

        # Plot clusters
        plt.figure(figsize=(8, 6))
        plt.scatter(pca_features[:, 0], pca_features[:, 1], c=y_kmeans, cmap='viridis')
        plt.title(f"2D Cluster Visualization (k=2)")
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 2")
        plt.show()

        ''' IN 3D '''

    for k in [2]:
        kmeans_model = KMeans(n_clusters=k, init='k-means++', random_state=53)
        
        # Reduce to 3 principal components
        pca = PCA(n_components=3)
        pca_features = pca.fit_transform(scaled_df)
        
        y_kmeans = kmeans_model.fit_predict(pca_features)
        
        print(f"Silhouette score for k={k}: {silhouette_score(pca_features, y_kmeans):.3f}")
        print(f"DBI for k={k}: {davies_bouldin_score(pca_features, y_kmeans):.3f}")

        # Create 3D plot with Seaborn styling
        plt.figure(figsize=(12, 8))
        ax = plt.axes(projection='3d')
        
        # Use Seaborn's 'husl' palette for better color differentiation
        palette = sns.color_palette("husl", n_colors=k)
        
        # Plot each cluster with distinct colors
        for i in range(k):
            ax.scatter3D(pca_features[y_kmeans == i, 0], 
                        pca_features[y_kmeans == i, 1], 
                        pca_features[y_kmeans == i, 2],
                        c=[palette[i]],
                        label=f'Cluster {i+1}',
                        s=60,  # Marker size
                        edgecolor='w',  # White edges for better visibility
                        alpha=0.8)  # Slight transparency
        
        # Add labels and title
        ax.set_xlabel('PC1', fontsize=12, labelpad=15)
        ax.set_ylabel('PC2', fontsize=12, labelpad=15)
        ax.set_zlabel('PC3', fontsize=12, labelpad=15)
        plt.title(f'3D Cluster Visualization (k={k})', fontsize=16, pad=20)
        
        # Add legend and grid
        ax.legend(fontsize=12, loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Set viewing angle for better perspective
        ax.view_init(elev=25, azim=45)  # Adjust these values as needed
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=sns.color_palette("husl", as_cmap=True))
        sm.set_array(y_kmeans)
        plt.colorbar(sm, ax=ax, pad=0.1, label='Cluster')
        
        # Use Seaborn style
        sns.set_style("whitegrid")
        sns.set_context("talk", font_scale=0.8)
        
        plt.tight_layout()
        plt.show()

        
        
def correlation_matrix(df):
    temp_df = df[['num_reactions','num_comments', 'num_shares','num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys']]
    display_table(temp_df)
    corr = temp_df.corr()
    plt.figure(figsize=(30,20), edgecolor="red")
    sns.heatmap(corr, fmt=".2f", annot=True, linewidths=1.5, xticklabels='auto', yticklabels='auto')
    plt.xticks(rotation=45)
    plt.yticks(rotation=45)
    plt.show()

def relation_bw_reaction_timestamp(df):
    temp_df = df[['hour_of_day', 'num_reactions']]
    display_table(temp_df)
    fig1 = plt.figure(figsize=(10,30) )
    sns.scatterplot(data=temp_df, x="hour_of_day", y="num_reactions")
    plt.title('Scatter Plot for Reactions by Hour of the Day')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Reactions')
    plt.xlim(0,24)

    fig2 = plt.figure(figsize=(10,20))
    sns.lineplot(data=temp_df, x="hour_of_day", y="num_reactions")
    plt.title('Line Plot for Reactions by Hour of the Day')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Reactions')
    plt.ylim(0,1000)
    plt.xlim(0,24)
    
    fig3 = plt.figure(figsize=(10,30))
    sns.scatterplot(data=df, x="month", y="num_reactions")
    plt.title('Scatter Plot for Reactions by Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Reactions')
    plt.xlim(0,13)


    fig4 = plt.figure(figsize=(10,30))
    sns.scatterplot(data=df, x="month", y="num_reactions")
    plt.title('Scatter Plot for Reactions by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Reactions')

    fig5 = plt.figure(figsize=(10,30))
    sns.lineplot(data=df, x="month", y="num_reactions")
    plt.title('Line Plot for Reactions by Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Reactions')
    plt.xlim(0,13)


    fig6 = plt.figure(figsize=(10,30))
    sns.lineplot(data=df, x="year", y="num_reactions")
    plt.title('Line Plot for Reactions by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Reactions')

    plt.show()

if __name__ == "__main__":
    main()