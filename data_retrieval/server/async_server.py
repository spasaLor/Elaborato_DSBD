import asyncio
import logging
from typing import AsyncIterable

import grpc
import retrieval_pb2
import retrieval_pb2_grpc
#----
import sys

#import per il db:
import mysql.connector as sql


class RetrievalService(retrieval_pb2_grpc.RetrievalServiceServicer):
    def __init__(self) -> None:
        super().__init__()
        
        # Connect to mysql
        try:
            self.cnx = sql.connect( 
                user="user",
                password="password",
                host="db", 
                database="test_dsbd")
            self.cursor = self.cnx.cursor()
        except sql.Error as e:
            print(f"Error connecting to Mysql DB: {e}")
            sys.exit(1)
    
    
    def __del__(self) -> None:
        self.cnx.close()
        
        
    async def GetDickeyFuller(
            self, request: retrieval_pb2.RetrievalRequest,
            context: grpc.aio.ServicerContext) -> retrieval_pb2.RetrievalDickeyFuller:
        self.cursor.execute(request.query)
        for result in self.cursor.fetchall():
            return retrieval_pb2.RetrievalDickeyFuller(
                    name=result[1], partition=result[2], test_statistic=result[3], 
                    p_value=result[4], is_stationary=result[5], crit_value1=result[6],
                    crit_value5=result[7], crit_value10=result[8])
        return retrieval_pb2.RetrievalDickeyFuller(
            name='', partition='',test_statistic=0, 
            p_value=0, is_stationary=0, crit_value1=0,
            crit_value5=0, crit_value10=0)
    
    
    async def ListDecomposition(
            self, request:retrieval_pb2.RetrievalRequest,
            context: grpc.aio.ServicerContext) -> AsyncIterable[retrieval_pb2.RetrievalDecomposition]:
        self.cursor.execute(request.query)
        for result in self.cursor.fetchall():
            yield retrieval_pb2.RetrievalDecomposition(
                    name=result[1], partition=result[2], timestamp=result[3].strftime('%d/%m/%Y, %H:%M:%S'), 
                    typology=result[4], value=result[5])
        yield retrieval_pb2.RetrievalDecomposition(
            name='', partition='', timestamp='', 
            typology='', value=0)
            
            
    async def ListHodrickPrescott(
            self, request:retrieval_pb2.RetrievalRequest,
            context: grpc.aio.ServicerContext) -> AsyncIterable[retrieval_pb2.RetrievalHodrickPrescott]:
        self.cursor.execute(request.query)
        for result in self.cursor.fetchall():
            yield retrieval_pb2.RetrievalHodrickPrescott(
                    name=result[1], partition=result[2], timestamp=result[3].strftime('%d/%m/%Y, %H:%M:%S'), 
                    value=result[4])
        yield retrieval_pb2.RetrievalHodrickPrescott(
                name='', partition='', timestamp='', 
                value=0)
            
            
    async def ListAutocorrelation(
            self, request:retrieval_pb2.RetrievalRequest,
            context: grpc.aio.ServicerContext) -> AsyncIterable[retrieval_pb2.RetrievalAutocorrelation]:
        self.cursor.execute(request.query)
        for result in self.cursor.fetchall():
            yield retrieval_pb2.RetrievalAutocorrelation(
                    name=result[1], partition=result[2], value=result[3])
        yield retrieval_pb2.RetrievalAutocorrelation(
                name='', partition='', value=0)
            
            
    async def ListAggregates(
            self, request:retrieval_pb2.RetrievalRequest,
            context: grpc.aio.ServicerContext) -> AsyncIterable[retrieval_pb2.RetrievalAggregates]:
        self.cursor.execute(request.query)
        for result in self.cursor.fetchall():
            yield retrieval_pb2.RetrievalAggregates(
                    name=result[1], partition=result[2], range=result[3],
                    typology=result[4], value=result[5], predicted_value=result[6])
        yield retrieval_pb2.RetrievalAggregates(
                name='', partition='', range='', 
                typology='', value=0, predicted_value=0)



async def serve() -> None:
    server = grpc.aio.server()
    retrieval_pb2_grpc.add_RetrievalServiceServicer_to_server(RetrievalService(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())


