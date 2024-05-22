import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DataSamplesRequest } from '../models/data-samples-request.model'

@Injectable({
  providedIn: 'root'
})
export class DataSampleService {

  private baseUrl = 'http://localhost:8080/api'; // backend URL

  constructor(private http: HttpClient) { }

  /*
  addGame(videoGame: VideoGame) {
  	console.log("example", videoGame)
    const gameData = VideoGameUtils.convertToGameData(videoGame);
    let params = new HttpParams()
    return this.http.get(`${this.baseUrl}/games/add-game`, {params});
  }*/

  getAllTasksets(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/configuration/tasksets`);
  }

  // Taskset Methods
  createTaskset(newTaskset: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/configuration/tasksets`, newTaskset);
  }

  // Assignment Methods
  getAllAssignments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/configuration/assignments`);
  }

  createAssignment(newAssignment: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/configuration/assignments`, newAssignment);
  }

  getAllSchedulings(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/configuration/schedulings`);
  }

  // Experience Parameters Methods
  getAllExperienceParameters(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/configuration/experiences`);
  }

  createExperience(newExperience: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/configuration/experiences`, newExperience);
  }

  updateExperience(id: number, experience: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/configuration/experiences/${id}`, experience);
  }
  
  deleteExperience(id: number): Observable<string> {
    return this.http.delete(`${this.baseUrl}/configuration/experiences/${id}`, {
      responseType: 'text'  // Expecting text response
    });
  }

  filterByTasksetId(tasksetId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/configuration/filterByTasksetId/${tasksetId}`);
  }

  filterByAssignmentId(assignmentId: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/configuration/filterByAssignmentId/${assignmentId}`);
  }

  executeScriptWithNumber(number: number): Observable<any> {
    const params = new HttpParams().set('number', number.toString());
    return this.http.post<any>(`${this.baseUrl}/configuration/execute`, null, { params });
  }


  getDashboardStatistics(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/datasample/statistics`);
  }

  getDataSamples(request: DataSamplesRequest): Observable<any> {
    console.log(request)
    return this.http.post<any>(`${this.baseUrl}/datasample`, request);
  }

  getDataSampleEnums(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/datasample/enums`);
  }

  createDataSample(dataSample: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/datasample/addSample`, dataSample);
  }

  updateDataSample(id: number, dataSample: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/datasample/${id}`, dataSample);
  }

  softDeleteDataSample(id: number): Observable<string> {
    return this.http.put(`${this.baseUrl}/datasample/softdelete/${id}`, null, {
      responseType: 'text'  // Expecting text response
    });
  }

  deleteDataSample(id: number): Observable<string> {
    return this.http.delete(`${this.baseUrl}/datasample/${id}`, {
      responseType: 'text'  // Expecting text response
    });
  }

  /*
  getGame(gameId: string) : Observable<any> {
    let params = new HttpParams()
    return this.http.get(`${this.baseUrl}/games/` + gameId, { params });
  }
  */

}
