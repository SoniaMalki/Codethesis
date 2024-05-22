import { Component } from '@angular/core';
import { SolarData } from '../../@core/data/solar';
import { OnDestroy} from '@angular/core';
import { NbThemeService } from '@nebular/theme';
import { takeWhile } from 'rxjs/operators' ;
import { SolarComponent } from './solar/solar.component' ;
import { DataSampleService } from '../../services/datasample.service';

@Component({
  selector: 'ngx-ecommerce',
  templateUrl: './e-commerce.component.html',
})
export class ECommerceComponent {
	solarValue: number;
	private alive = true;

  dashboardStatistics: any;

  totalProcessed: number;
  totalSamples: number;
  percentageProcessed: number;

  numberDataSample: number;
  totalDataSampleObjective: number;
  percentageDataSample: number;

  objectiveToken: number;
  totalTokenFrench: number;
  percentageTokenFrench: number;
  totalTokenEnglish: number;
  percentageTokenEnglish: number;

  averageQuality: number;
  qualityDistribution: any[];

  averagePositivity: number;
  positivityDistribution: any[];

  sourcesPercentages: any;
  referencesPercentages: any;

  estimationRemainingInfoData: any[];
  weeklyObjectiveInfoData: any[];

  estimatedDaysToReachObjectiveToken: number

  categories: any[] = [];

	constructor(private themeService: NbThemeService, private solarService: SolarData, public dataSampleService: DataSampleService) {

		this.fetchDashboardStatistics();
  	this.solarService.getSolarData()
      .pipe(takeWhile(() => this.alive))
      .subscribe((data) => {
        this.solarValue = data;
      });
	 }

private fetchDashboardStatistics(): void {
    this.dataSampleService.getDashboardStatistics().subscribe({
        next: (statistics) => {
            this.dashboardStatistics = statistics;
            console.log('Dashboard Statistics:', statistics);
            this.totalProcessed = this.formatNumber(statistics.processedDataSamples);
            this.totalSamples = this.formatNumber(statistics.totalDataSamples);
            this.percentageProcessed = this.formatNumber((this.totalProcessed / statistics.totalDataSampleObjective) * 100);

            this.numberDataSample = this.formatNumber(statistics.totalDataSamples);
            this.totalDataSampleObjective = this.formatNumber(statistics.totalDataSampleObjective);
            this.percentageDataSample = this.formatNumber((this.numberDataSample / this.totalDataSampleObjective) * 100);

            this.objectiveToken = this.formatNumber(statistics.totalTokensObjective);
            this.totalTokenFrench = this.formatNumber(statistics.totalTokensFrench);
            this.percentageTokenFrench = this.formatNumber((this.totalTokenFrench / this.objectiveToken) * 100);
            this.totalTokenEnglish = this.formatNumber(statistics.totalTokensEnglish);
            this.percentageTokenEnglish = this.formatNumber((this.totalTokenEnglish / this.objectiveToken) * 100);

            this.averageQuality = this.formatNumber(statistics.meanQuality*100)
            this.qualityDistribution = statistics.qualityDistribution
            this.averagePositivity = this.formatNumber(statistics.meanPositivityRating*100)
            this.positivityDistribution = statistics.positivityDistribution

            const last14DaysTokens = statistics.last14DaysFrenchTokens

            // Calculate total tokens added in the last 14 days
            const totalTokensLast14Days = last14DaysTokens.reduce((sum, day) => {
                return sum + Object.values(day)[0];
            }, 0);


            console.log(last14DaysTokens.length);

            // Calculate average tokens added per day
            const averageTokensPerDay = totalTokensLast14Days / last14DaysTokens.length;

            // Calculate remaining tokens required to reach the objective
            const remainingTokens = this.objectiveToken - statistics.totalTokensFrench;

            // Calculate estimated days to reach the objective
            const estimatedDaysToReachObjective = Math.ceil(remainingTokens / averageTokensPerDay);

            console.log('Average Tokens Per Day:', averageTokensPerDay);
            console.log('Estimated Days to Reach Objective:', estimatedDaysToReachObjective);




            const last14DaysProcessed = statistics.last14DaysProcessedSamples

            // Calculate total tokens added in the last 14 days
            const totalProcessedLast14Days = last14DaysProcessed.reduce((sum, day) => {
                return sum + Object.values(day)[0];
            }, 0);


            console.log(last14DaysProcessed.length);

            // Calculate average tokens added per day
            const averageProcessedPerDay = totalProcessedLast14Days / last14DaysProcessed.length;

            // Calculate remaining tokens required to reach the objective
            const remainingToProcess = statistics.totalDataSampleObjective - this.numberDataSample

            // Calculate estimated days to reach the objective
            const estimatedDaysToReachSampleObjective = Math.ceil(remainingToProcess / averageProcessedPerDay);

            console.log('Average Processed Per Day:', averageProcessedPerDay);
            console.log('Estimated Days to Reach Processed Objective:', estimatedDaysToReachSampleObjective);

            this.estimationRemainingInfoData = [
              {
                  title: 'Estimated remaining days (tokens)',
                  value: estimatedDaysToReachObjective,
                  activeProgress: 100,
                  description: '',
                },
                {
                  title: 'Estimated remaining days (samples)',
                  value: estimatedDaysToReachSampleObjective,
                  activeProgress: 100,
                  description: '',
                },
            ]

            

            // Extract the last 7 days' data
            const last7DaysFrenchTokens = statistics.last14DaysFrenchTokens.slice(0, 7);
            const last7DaysProcessedSamples = statistics.last14DaysProcessedSamples.slice(0, 7);

            // Calculate total tokens added in the last 7 days
            const totalTokensLast7Days = last7DaysFrenchTokens.reduce((sum, day) => {
              return sum + Object.values(day)[0];
            }, 0);

            // Calculate total processed samples in the last 7 days
            const totalProcessedLast7Days = last7DaysProcessedSamples.reduce((sum, day) => {
              return sum + Object.values(day)[0];
            }, 0);

            
            const objectiveTokenPerWeek = statistics.objectiveTokenPerDay * 7
            const objectiveProcessedPerWeek = statistics.objectiveProcessPerDay * 7
            // Calculate weekly percentages achieved
            const tokensWeeklyPercentage = (totalTokensLast7Days / objectiveTokenPerWeek) * 100;
            const processedWeeklyPercentage = (totalProcessedLast7Days / objectiveProcessedPerWeek) * 100;

            this.weeklyObjectiveInfoData = [
              {
                  title: 'Weekly Tokens objective',
                  value: totalTokensLast7Days,
                  activeProgress: tokensWeeklyPercentage,
                  description: 'out of expected '+ objectiveTokenPerWeek +' ('+this.formatNumber(tokensWeeklyPercentage)+'%)',
                },
                {
                  title: 'Weekly Processed Samples objective',
                  value: totalProcessedLast7Days,
                  activeProgress: processedWeeklyPercentage,
                  description: 'out of expected '+ objectiveProcessedPerWeek +' ('+this.formatNumber(processedWeeklyPercentage)+'%)',
                },
            ]


            // Calculate Source Percentages
            const sourceStatistics = statistics.sourceStatistics;
            const totalSourceValue = (Object.values(sourceStatistics) as number[]).reduce((acc, val) => acc + val, 0);

            // Calculate percentages for each source
            const sourcePercentages = Object.entries(sourceStatistics).reduce((acc, [key, value]) => {
                acc[key] = Math.round((value as number / totalSourceValue) * 100);
                return acc;
            }, {} as { [key: string]: number });

            this.sourcesPercentages = sourcePercentages

            // Calculate Source Percentages
            const referenceStatistics = statistics.referenceStatistics;
            const totalReferenceValue = (Object.values(referenceStatistics) as number[]).reduce((acc, val) => acc + val, 0);

            // Calculate percentages for each source
            const referencePercentages = Object.entries(referenceStatistics).reduce((acc, [key, value]) => {
                acc[key] = Math.round((value as number / totalReferenceValue) * 100);
                return acc;
            }, {} as { [key: string]: number });

            this.referencesPercentages = referencePercentages
            console.log(sourcePercentages)
            console.log(referencePercentages)

            console.log('Dashboard Statistics:', statistics);
        },
        error: (error) => {
            console.error('Error fetching dashboard statistics:', error);
        }
    });
}

  formatNumber(value: number): number {
    // Format the value to one decimal place using toFixed
    const formatted = value.toFixed(1);
    // Convert the string back to a number
    return parseFloat(formatted);
}

}
