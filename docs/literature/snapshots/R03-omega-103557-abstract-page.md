[![Omega](https://ars.els-cdn.com/content/image/1-s2.0-S0305048326X20023-cov200h.gif)](/journal/omega/vol/143/suppl/C)

## Published by: Elsevier

### Published by

[![Elsevier](/us-east-1/prod/889670af36b5044091281d5e1d000b53155c5cd5/image/elsevier-non-solus.svg)](/journal/omega)

Research article

# Prescriptive analytics for hospital drug inventory: A context-aware multi-channel neural network for integrated forecasting and optimization☆

Author links open overlay panel, ,

## Highlights

- •
A novel framework unifies drug demand forecasting and inventory decisions.
- •
Context-aware model integrates weather, search trends, and demographics.
- •
A neural network learns from a loss function based on inventory costs.
- •
Reduces total inventory costs compared to traditional two-stage methods.

## Keywords

Prescriptive analytics

;
Inventory decision-making

;
Demand forecasting

;
Multi-channel neural network

;
Multi-source data

## Introduction

Effective management of pharmaceutical inventories in hospitals is a critical and complex challenge that directly impacts patient outcomes, supply chain responsiveness, and cost control within healthcare systems [1]. Unlike conventional inventory settings, hospital pharmaceutical supply chains face volatile and often unpredictable demand [2]. This variability is influenced by diverse and dynamic factors such as seasonal meteorological patterns [3], [4], regional demographic shifts [5], [6], clinical records [2], and public sentiment revealed in online search behavior [7]. The integration of these multifaceted data sources increases the complexity of demand forecasting and decision-making [8]. Poor synthesis or utilization of such information can result in drug stockouts – delaying treatment delivery – or excessive ordering of perishable pharmaceuticals, leading to financial waste and inefficiency [9].

While accurate demand forecasting is essential, it alone is insufficient for effective inventory management. Classical operations research methods such as stochastic optimization [10] and sample average approximation [11] often assume known or well-approximated demand distributions, but fail to leverage auxiliary covariates such as environmental, behavioral, or epidemiological signals. Conversely, machine learning models – including regression, random forests, and neural networks [12] – excel at capturing complex predictive patterns from such data but typically optimize for predictive accuracy, not decision outcomes. This disconnect may lead to suboptimal decisions, particularly under cost-sensitive or risk-sensitive scenarios. From a statistical decision theory perspective [13], [14], good predictions do not guarantee good decisions unless the loss function is explicitly calibrated to operational objectives. Recent advances in task-based or decision-aware learning seek to address this gap by minimizing losses defined over decision performance rather than predictive error alone [15], [16]. This emerging paradigm is unified under the framework of contextual optimization [17], particularly the Integrated Learning and Optimization framework, which focuses on searching for the predictive model that best guides the associated optimization problem toward high-quality prescribed actions. These developments motivate an integrated approach that unifies forecasting and decision-making through a common objective tailored to cost or service-level considerations.

Although considerable progress has been made in recent years, hospital pharmaceutical inventory management still leaves critical issues insufficiently addressed, particularly in two areas: (1) How can multi-source data – including historical ordering records, epidemiological indicators, weather conditions, online behavioral signals, and demographic factors – be effectively synthesized to improve demand forecasting accuracy in hospital pharmaceutical inventory systems? (2) How can demand forecasting be integrated with inventory decision-making to enhance cost efficiency under uncertainty?

In what follows, we review existing literature from two main perspectives: demand forecasting and inventory decision-making. With respect to demand forecasting, traditional statistical methods such as time series analysis and regression models have been extensively utilized for pharmaceutical requirements estimation. These approaches are widely employed but inherently assume demand regularity, rendering them inadequate for capturing abrupt fluctuations resulting from emergencies or pandemics, with stockout rates documented as high as 85.6% in certain hospital facilities [18], [19]. Moreover, prevailing practices in the pharmaceutical industry predominantly rely on historical demand data, with limited integration of auxiliary supply chain information such as downstream inventory information and supply chain structure information [20]. This disconnect further complicates inventory management at the hospital level, where demand patterns are highly sensitive to contextual and epidemiological signals. For instance, during the COVID-19 pandemic, conventional forecasting models failed to anticipate the unprecedented surge in demand for critical medications, resulting in widespread shortages [21], [22].

In response, machine learning techniques—such as random forests and neural networks have gained popularity for their ability to model complex nonlinear relationships [23]. Berktas et al. [24] suggest that artificial intelligence can enhance forecasting performance by leveraging diverse variables – including historical trends, seasonal patterns, epidemiological data, and patient preferences – contributing to improved supply–demand coordination and mitigating stockout risks. However, many existing studies still overlook relevant signals such as clinical records or social sentiment data, limiting their ability to capture sudden shifts in demand [7], [8]. Overall, while neural networks and other learning-based methods show promise, more comprehensive integration of contextual features remains a gap in current pharmaceutical demand forecasting research.

Turning to inventory decision-making, classical normative models – including the Economic Order Quantity and rule-based heuristics – remain widely used for balancing cost and service levels [25]. These models have shown measurable benefits, with reported cost savings of up to $220,500 in some healthcare settings [26]. However, their assumptions of stable demand and fixed lead times are often violated in hospital environments [27].

While data-driven approaches have been developed to improve inventory control [2], [27], [28], [29], [30], [31], [32], most frameworks still rely on two-stage architectures that decouple demand forecasting and replenishment decisions. This structural separation tends to amplify prediction errors and degrade inventory performance—especially under demand surges or supply interruptions. For example, studies have reported stockout or overstock rates reaching up to 50.6% when forecasting outputs are not well integrated into the decision-making layer [19]. To overcome such decoupling, reinforcement learning has been explored as a unified decision-making paradigm in healthcare operations management [33] and broader supply chain contexts [34]; however, its data-hungry nature and limited interpretability constrain its practical adoption in clinical environments where sample sizes are modest and decision transparency is essential. These limitations necessitate more tailored integrated frameworks.

Prescriptive analytics frameworks – which integrate predictive models, optimization techniques, and expert knowledge – have emerged as a promising solution for supporting data-driven decision-making under uncertainty [35]. Recent innovations such as Smart Predict-then-Optimize [15] and data-driven optimization frameworks [16] focus on minimizing decision loss rather than prediction error by embedding auxiliary information directly into optimization tasks. Extending this line of work on feature-based decision-making, recent research has leveraged Wasserstein distributionally robust optimization to construct optimal robust policies for the feature-based newsvendor problem, providing an end-to-end framework that maps contextual features directly to ordering decisions while effectively generalizing in-sample policies to unobserved feature values through Lipschitz regularization [36]. Although direct applications of these feature-based decision-making frameworks in hospital pharmaceutical contexts remain scarce, they provide valuable methodological insights for the integration of heterogeneous data sources in pharmaceutical inventory decision-making.

Recent research has examined the use of multi-source data for demand forecasting in pharmaceutical contexts [20], [37], but very few studies propose cohesive frameworks that jointly optimize forecasting and decision-making. Among them, Galli et al. [38] develop a prescriptive analytics model for hospital pharmacies that incorporates ward-level patient records and dosing data. While their work demonstrates improvements in emergency ordering and inventory holding, it remains limited to inpatient pharmacy operations and does not incorporate external contextual variables. In addition, this model employs a non-parametric, locally weighted prediction approach inspired by Bertsimas and Kallus [16], but does not implement an integrated learning architecture that directly connects forecasting outputs with inventory decisions. Qi et al. [39] propose a novel one-step end-to-end framework to address the multiperiod inventory replenishment problem. Their work serves as a powerful practical example of prescriptive analytics, designing a deep learning neural network structure that directly maps a wide array of heterogeneous features – such as item attributes, promotions, and historical data – to replenishment decisions. This end-to-end approach thereby eliminates the need to separately formulate and solve a traditional inventory model. The framework’s successful large-scale implementation in [JD.com](http://JD.com) validates its strong performance in consumer-facing retail environments characterized by high demand volatility and promotional sensitivity. This end-to-end architecture is being extended to more complex scenarios, such as the deep fusion framework that employs graph convolutional networks to model inter-product dependencies [40], and distribution-free models for substitutable inventory control that utilize re-engineered loss functions to directly output procurement decisions [41]. However, a dedicated framework that effectively couples multi-source data with the specific asymmetric cost structures of hospital pharmacy remains an area requiring further integration.

In this paper, we propose a prescriptive analytics framework for hospital drug inventory management that tightly integrates demand forecasting and inventory decision-making. At the core of our approach lies an integrated learning architecture called *Multi-Channel model for Integrated Forecasting and Optimization* (MC-IFO) that directly couples forecasting with inventory optimization, realized by a context-aware multi-channel neural network whose loss function explicitly minimizes expected inventory costs through asymmetric penalty functions for overstocking and understocking. This design ensures that forecasting accuracy is not treated as an isolated objective, but directly supports the overarching goal of minimizing operational costs. The effectiveness of the proposed framework is validated through theoretical analysis and numerical experiments, including comparisons against both single-channel and two-stage baselines. The results underscore the advantages of incorporating heterogeneous data sources and structuring the learning process around decision-centric objectives in hospital inventory management.

This research makes two contributions:

- •
First, we develop a flexible multi-channel neural network architecture capable of integrating heterogeneous data sources – including historical demand, weather conditions, search engine trends, and demographic indicators – thus enabling context-aware demand forecasting. Comparative experiments further demonstrate that leveraging multiple data streams consistently outperforms single-channel models, both in predictive accuracy and cost reduction.
- •
Second, we propose an integrated prediction-decision framework that jointly optimizes forecasting and ordering decisions. Unlike the traditional two-stage approach – which first minimizes prediction error and then solves an optimization problem – we embed the inventory cost structure, characterized by asymmetric overage and underage costs, directly into the learning process. We provide theoretical guarantees that this integrated method achieves a lower or equal expected cost compared to the two-stage benchmark.

The remainder of the paper is structured as follows: Section 2 formulates the problem and presents the analytical framework. Section 3 details the proposed MC-IFO model, covering its network architecture development and the optimization approach. Section 4 describes the experimental design and results. Section 5 concludes the paper.

## Section snippets

### Problem description

In this work, we consider the inventory management problem with stochastic demand. Unlike general commodities, pharmaceutical products possess unique characteristics such as perishability and critical service level requirements, where a stockout can directly impact patient health. These attributes underline the importance of a precise and responsive inventory policy. The details are shown as follows: for a single item at a single hospital, we consider a horizon of discrete periods 1,…,T. We

### Overview of the MC-IFO framework

Fig. 2 presents the architecture of the proposed MC-IFO model, which unifies demand forecasting and inventory decision-making into a prescriptive framework. The model processes diverse contextual data through specialized network channels, enabling optimization of ordering quantities with respect to cost-related objectives.

The overall structure is illustrated in the upper dashed box of Fig. 2, comprising four major components: (1) input modules for different categories of time-series data,

### Experimental setup and data description

This study utilizes four categories of weekly data collected from Beijing in 2018: demand records, hospital statistics, meteorological indicators, and web search trends. The demand data are obtained from Heywhale, a data science platform providing publicly available datasets. Hospital data comprise weekly counts of respiratory infection cases reported through the Beijing CDC monitoring network, supplemented with population density statistics from the Beijing Statistical Yearbook. Meteorological

### Conclusion

Effective inventory management for hospital pharmaceuticals is a critical operational challenge, directly impacting both patient care and financial sustainability. The inherent demand uncertainty, coupled with the high costs associated with stockouts and wastage, necessitates sophisticated decision-support systems. This study addressed this challenge by developing a prescriptive analytics framework, the *Multi-Channel model for Integrated Forecasting and Optimization* (MC-IFO), which tightly

### CRediT authorship contribution statement

**Jie Chen:** Writing – review & editing, Writing – original draft, Visualization, Validation, Software, Methodology, Investigation, Formal analysis, Data curation, Conceptualization. **Zeshui Xu:** Writing – review & editing. **Bin Zhu:** Writing – review & editing, Supervision, Resources, Project administration, Formal analysis, Investigation, Conceptualization.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgments

This work was supported by the Yunnan Provincial Academician and Expert Workstation (Project No. 202505AF350054). The authors also acknowledge the support of the High Performance Computing Center, Yangtze Delta Region Academy of Beijing Institute of Technology, Jiaxing .

- **☆** Area: Data-Driven Optimization. This manuscript was processed by Associate Editor Vera Tilson.

[View full text](/science/article/pii/S0305048326000460)

© 2026 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.